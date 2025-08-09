from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class Movie(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tmdb_id: int
    title: str
    description: str
    genre: List[str]
    year: int
    rating: float
    poster_url: str
    backdrop_url: str
    trailer_url: Optional[str] = None
    type: str  # 'movie' or 'tv'
    categories: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MovieResponse(BaseModel):
    tmdb_id: int
    title: str
    description: str
    genre: List[str]
    year: int
    rating: float
    poster_url: str
    backdrop_url: str
    trailer_url: Optional[str] = None
    type: str

class WatchlistRequest(BaseModel):
    movie_id: int