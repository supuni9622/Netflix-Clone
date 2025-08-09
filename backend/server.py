from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import timedelta

# Import models
from models.user import User, UserCreate, UserLogin, UserProfile
from models.movie import MovieResponse, WatchlistRequest

# Import services
from services.tmdb_service import tmdb_service
from services.auth_service import auth_service, ACCESS_TOKEN_EXPIRE_MINUTES

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    token = credentials.credentials
    user_id = auth_service.verify_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

# Optional auth dependency
async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[User]:
    if credentials is None:
        return None
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None

# Authentication endpoints
@api_router.post("/auth/register")
async def register_user(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = auth_service.get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password
    )
    
    await db.users.insert_one(user.dict())
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserProfile(
            id=user.id,
            username=user.username,
            email=user.email,
            watchlist=user.watchlist,
            created_at=user.created_at
        )
    }

@api_router.post("/auth/login")
async def login_user(login_data: UserLogin):
    # Find user by email
    user_doc = await db.users.find_one({"email": login_data.email})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user = User(**user_doc)
    
    # Verify password
    if not auth_service.verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserProfile(
            id=user.id,
            username=user.username,
            email=user.email,
            watchlist=user.watchlist,
            created_at=user.created_at
        )
    }

@api_router.get("/auth/profile", response_model=UserProfile)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    return UserProfile(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        watchlist=current_user.watchlist,
        created_at=current_user.created_at
    )

# Movie endpoints
@api_router.get("/movies/categories")
async def get_movie_categories():
    try:
        categories = await tmdb_service.get_categories()
        return {"categories": categories}
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch movie categories")

@api_router.get("/movies/trending")
async def get_trending_movies():
    try:
        movies = await tmdb_service.get_trending_movies()
        tv_shows = await tmdb_service.get_trending_tv()
        return {"movies": movies + tv_shows}
    except Exception as e:
        logger.error(f"Error getting trending movies: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch trending movies")

@api_router.get("/movies/popular")
async def get_popular_movies():
    try:
        movies = await tmdb_service.get_popular_movies()
        tv_shows = await tmdb_service.get_popular_tv()
        return {"movies": movies + tv_shows}
    except Exception as e:
        logger.error(f"Error getting popular movies: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch popular movies")

@api_router.get("/movies/search")
async def search_movies(q: str):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    
    try:
        results = await tmdb_service.search_content(q)
        return {"results": results}
    except Exception as e:
        logger.error(f"Error searching movies: {e}")
        raise HTTPException(status_code=500, detail="Failed to search movies")

@api_router.get("/movies/{movie_id}")
async def get_movie_details(movie_id: int, media_type: str = "movie"):
    try:
        movie = await tmdb_service.get_movie_details(movie_id, media_type)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        return movie
    except Exception as e:
        logger.error(f"Error getting movie details: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch movie details")

# Watchlist endpoints
@api_router.post("/movies/{movie_id}/watchlist")
async def add_to_watchlist(movie_id: int, current_user: User = Depends(get_current_user)):
    try:
        # Check if movie is already in watchlist
        if movie_id in current_user.watchlist:
            return {"message": "Movie already in watchlist"}
        
        # Add to watchlist
        await db.users.update_one(
            {"id": current_user.id},
            {"$push": {"watchlist": movie_id}}
        )
        
        return {"message": "Movie added to watchlist"}
    except Exception as e:
        logger.error(f"Error adding to watchlist: {e}")
        raise HTTPException(status_code=500, detail="Failed to add movie to watchlist")

@api_router.delete("/movies/{movie_id}/watchlist")
async def remove_from_watchlist(movie_id: int, current_user: User = Depends(get_current_user)):
    try:
        # Remove from watchlist
        await db.users.update_one(
            {"id": current_user.id},
            {"$pull": {"watchlist": movie_id}}
        )
        
        return {"message": "Movie removed from watchlist"}
    except Exception as e:
        logger.error(f"Error removing from watchlist: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove movie from watchlist")

@api_router.get("/users/watchlist")
async def get_user_watchlist(current_user: User = Depends(get_current_user)):
    try:
        watchlist_movies = []
        for movie_id in current_user.watchlist:
            # Try to get movie details from TMDB
            movie = await tmdb_service.get_movie_details(movie_id, "movie")
            if not movie:
                # Try as TV show
                movie = await tmdb_service.get_movie_details(movie_id, "tv")
            
            if movie:
                watchlist_movies.append(movie)
        
        return {"watchlist": watchlist_movies}
    except Exception as e:
        logger.error(f"Error getting watchlist: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch watchlist")

# Health check
@api_router.get("/")
async def root():
    return {"message": "Netflix Clone API is running"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()