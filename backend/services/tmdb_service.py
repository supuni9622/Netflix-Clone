import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class TMDBService:
    def __init__(self):
        self.api_keys = [
            "c8dea14dc917687ac631a52620e4f7ad",
            "3cb41ecea3bf606c56552db3d17adefd"
        ]
        self.current_key_index = 0
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/w500"
        self.backdrop_base_url = "https://image.tmdb.org/t/p/w1280"
        
    def get_current_api_key(self) -> str:
        return self.api_keys[self.current_key_index]
    
    def rotate_api_key(self):
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
    
    async def make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        if params is None:
            params = {}
        params['api_key'] = self.get_current_api_key()
        
        async with aiohttp.ClientSession() as session:
            for attempt in range(len(self.api_keys)):
                try:
                    async with session.get(f"{self.base_url}{endpoint}", params=params) as response:
                        if response.status == 429:  # Rate limited
                            self.rotate_api_key()
                            params['api_key'] = self.get_current_api_key()
                            continue
                        elif response.status == 200:
                            return await response.json()
                        else:
                            logger.warning(f"TMDB API returned status {response.status}")
                            return None
                except Exception as e:
                    logger.error(f"TMDB API request failed: {e}")
                    self.rotate_api_key()
                    params['api_key'] = self.get_current_api_key()
                    if attempt == len(self.api_keys) - 1:
                        return None
        return None
    
    def format_movie(self, movie_data: Dict[str, Any], media_type: str = "movie") -> Dict[str, Any]:
        """Format TMDB movie data to our format"""
        title = movie_data.get('title') or movie_data.get('name', 'Unknown Title')
        description = movie_data.get('overview', 'No description available')
        
        # Get release year
        release_date = movie_data.get('release_date') or movie_data.get('first_air_date', '')
        year = int(release_date.split('-')[0]) if release_date else 2023
        
        # Get genres (if available)
        genres = []
        if 'genres' in movie_data:
            genres = [genre['name'] for genre in movie_data['genres']]
        elif 'genre_ids' in movie_data:
            # Map genre IDs to names (simplified)
            genre_map = {
                28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy",
                80: "Crime", 99: "Documentary", 18: "Drama", 10751: "Family",
                14: "Fantasy", 36: "History", 27: "Horror", 10402: "Music",
                9648: "Mystery", 10749: "Romance", 878: "Science Fiction",
                10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western"
            }
            genres = [genre_map.get(gid, "Unknown") for gid in movie_data.get('genre_ids', [])]
        
        # Calculate rating percentage
        vote_average = movie_data.get('vote_average', 0)
        rating = int(vote_average * 10) if vote_average else 75
        
        return {
            'tmdb_id': movie_data.get('id'),
            'title': title,
            'description': description,
            'genre': genres,
            'year': year,
            'rating': rating,
            'poster_url': f"{self.image_base_url}{movie_data.get('poster_path', '')}" if movie_data.get('poster_path') else "",
            'backdrop_url': f"{self.backdrop_base_url}{movie_data.get('backdrop_path', '')}" if movie_data.get('backdrop_path') else "",
            'type': media_type,
            'trailer_url': None  # Will be populated separately if needed
        }
    
    async def get_trending_movies(self) -> List[Dict[str, Any]]:
        """Get trending movies"""
        data = await self.make_request("/trending/movie/week")
        if data and 'results' in data:
            return [self.format_movie(movie, "movie") for movie in data['results'][:20]]
        return []
    
    async def get_trending_tv(self) -> List[Dict[str, Any]]:
        """Get trending TV shows"""
        data = await self.make_request("/trending/tv/week")
        if data and 'results' in data:
            return [self.format_movie(show, "tv") for show in data['results'][:20]]
        return []
    
    async def get_popular_movies(self) -> List[Dict[str, Any]]:
        """Get popular movies"""
        data = await self.make_request("/movie/popular")
        if data and 'results' in data:
            return [self.format_movie(movie, "movie") for movie in data['results'][:20]]
        return []
    
    async def get_popular_tv(self) -> List[Dict[str, Any]]:
        """Get popular TV shows"""
        data = await self.make_request("/tv/popular")
        if data and 'results' in data:
            return [self.format_movie(show, "tv") for show in data['results'][:20]]
        return []
    
    async def get_movies_by_genre(self, genre_id: int, media_type: str = "movie") -> List[Dict[str, Any]]:
        """Get movies by genre"""
        endpoint = f"/{media_type}/popular"
        params = {"with_genres": genre_id}
        data = await self.make_request(endpoint, params)
        if data and 'results' in data:
            return [self.format_movie(item, media_type) for item in data['results'][:20]]
        return []
    
    async def search_content(self, query: str) -> List[Dict[str, Any]]:
        """Search for movies and TV shows"""
        results = []
        
        # Search movies
        movie_data = await self.make_request("/search/movie", {"query": query})
        if movie_data and 'results' in movie_data:
            results.extend([self.format_movie(movie, "movie") for movie in movie_data['results'][:10]])
        
        # Search TV shows
        tv_data = await self.make_request("/search/tv", {"query": query})
        if tv_data and 'results' in tv_data:
            results.extend([self.format_movie(show, "tv") for show in tv_data['results'][:10]])
        
        return results[:20]
    
    async def get_movie_details(self, movie_id: int, media_type: str = "movie") -> Optional[Dict[str, Any]]:
        """Get detailed information about a movie or TV show"""
        endpoint = f"/{media_type}/{movie_id}"
        data = await self.make_request(endpoint)
        if data:
            movie_details = self.format_movie(data, media_type)
            
            # Get trailer URL
            trailer_url = await self.get_trailer_url(movie_id, media_type)
            movie_details['trailer_url'] = trailer_url
            
            return movie_details
        return None
    
    async def get_trailer_url(self, movie_id: int, media_type: str = "movie") -> Optional[str]:
        """Get YouTube trailer URL for a movie or TV show"""
        endpoint = f"/{media_type}/{movie_id}/videos"
        data = await self.make_request(endpoint)
        
        if data and 'results' in data:
            # Find YouTube trailer
            for video in data['results']:
                if (video.get('type') == 'Trailer' and 
                    video.get('site') == 'YouTube'):
                    return f"https://www.youtube.com/watch?v={video.get('key')}"
        return None
    
    async def get_categories(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get categorized content"""
        categories = {}
        
        # Get different categories
        trending_movies = await self.get_trending_movies()
        trending_tv = await self.get_trending_tv()
        popular_movies = await self.get_popular_movies()
        popular_tv = await self.get_popular_tv()
        
        # Action movies (genre ID: 28)
        action_movies = await self.get_movies_by_genre(28, "movie")
        
        # Comedy movies (genre ID: 35)
        comedy_movies = await self.get_movies_by_genre(35, "movie")
        
        categories = {
            "Trending Now": trending_movies + trending_tv,
            "Popular Movies": popular_movies,
            "Popular TV Shows": popular_tv,
            "Action & Adventure": action_movies,
            "Comedy": comedy_movies
        }
        
        return categories

# Create global instance
tmdb_service = TMDBService()