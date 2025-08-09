# Netflix Clone Backend Contracts

## API Contracts

### Movies/TV Shows Endpoints
```
GET /api/movies/trending - Get trending movies
GET /api/movies/popular - Get popular movies
GET /api/movies/categories - Get all movie categories
GET /api/movies/search?q={query} - Search movies/shows
GET /api/movies/{id} - Get movie details
POST /api/movies/{id}/watchlist - Add to user's watchlist
DELETE /api/movies/{id}/watchlist - Remove from user's watchlist
```

### User Management Endpoints
```
POST /api/auth/register - User registration
POST /api/auth/login - User login
GET /api/auth/profile - Get user profile
PUT /api/auth/profile - Update user profile
GET /api/users/watchlist - Get user's watchlist
```

### External Integration
```
TMDB API Integration:
- Fetch real movie/TV show data
- Get movie posters and backdrops
- Search functionality
- Get trending and popular content
- Get YouTube trailer URLs
```

## Mock Data to Replace

### Current Mock Data in /app/frontend/src/data/mockData.js:
1. **Movie Categories**: Trending Now, Popular on Netflix, New Releases, Action & Adventure
2. **Movie Objects**: id, title, description, genre, year, rating, poster, backdrop
3. **Featured Movie**: Hero section content

### Backend Data Structure:
```javascript
Movie/Show Schema:
{
  tmdb_id: Number,
  title: String,
  description: String,
  genre: [String],
  year: Number,
  rating: Number,
  poster_url: String,
  backdrop_url: String,
  trailer_url: String,
  type: String, // 'movie' or 'tv'
  categories: [String],
  created_at: Date
}

User Schema:
{
  username: String,
  email: String,
  password: String (hashed),
  watchlist: [ObjectId],
  created_at: Date
}
```

## Backend Implementation Plan

### 1. TMDB API Integration Service
- Fetch trending, popular, and category-based content
- Search functionality
- Get movie details with trailers
- Image URL management
- Rate limiting and caching

### 2. Database Models
- Movie/Show model for storing TMDB data
- User model for authentication
- Watchlist management

### 3. Authentication System
- JWT-based authentication
- User registration/login
- Protected routes for user-specific data

### 4. Business Logic
- Content categorization
- Watchlist management
- User preferences
- Search and filtering

## Frontend Integration Plan

### Replace Mock Data:
1. **Remove mockData.js imports** from NetflixHome.jsx
2. **Add API service layer** for HTTP requests
3. **Update state management** to fetch from backend
4. **Add authentication context** for user management
5. **Implement error handling** for API failures
6. **Add loading states** for better UX

### API Service Structure:
```javascript
// services/api.js
- getMovieCategories()
- searchMovies(query)
- getMovieDetails(id)
- addToWatchlist(movieId)
- removeFromWatchlist(movieId)
- getUserWatchlist()
```

### State Management Updates:
- Loading states for movie data
- Error handling for failed requests
- User authentication state
- Watchlist state management

## Integration Steps

1. **Backend Development**:
   - Set up TMDB API integration
   - Create MongoDB models
   - Implement CRUD endpoints
   - Add authentication middleware

2. **Frontend Integration**:
   - Create API service layer
   - Replace mock data with API calls
   - Add authentication context
   - Update components to handle loading/error states

3. **Testing & Validation**:
   - Test all API endpoints
   - Verify frontend-backend integration
   - Test user authentication flow
   - Validate watchlist functionality

## TMDB API Keys Available:
- c8dea14dc917687ac631a52620e4f7ad
- 3cb41ecea3bf606c56552db3d17adefd

## Expected Outcome
A fully functional Netflix clone with:
- Real movie/TV show data from TMDB
- User authentication and profiles
- Watchlist functionality
- Search capabilities
- Responsive design with authentic Netflix experience