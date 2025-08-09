import React, { useState, useEffect } from 'react';
import { Play, Info, Search, Bell, User, ChevronLeft, ChevronRight, Plus, ThumbsUp, ThumbsDown, Loader2, LogOut } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Badge } from './ui/badge';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from './ui/dropdown-menu';
import { useToast } from '../hooks/use-toast';
import { useAuth } from '../contexts/AuthContext';
import { moviesAPI } from '../services/api';
import AuthModal from './AuthModal';

const NetflixHome = () => {
  const [featuredMovie, setFeaturedMovie] = useState(null);
  const [movieCategories, setMovieCategories] = useState([]);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const { toast } = useToast();
  const { user, isAuthenticated, logout } = useAuth();

  useEffect(() => {
    loadMovieCategories();
  }, []);

  const loadMovieCategories = async () => {
    try {
      setIsLoading(true);
      const data = await moviesAPI.getCategories();
      
      if (data.categories) {
        // Convert categories object to array format for easier rendering
        const categoriesArray = Object.entries(data.categories).map(([name, movies]) => ({
          name,
          movies
        }));
        
        setMovieCategories(categoriesArray);
        
        // Set featured movie from trending
        if (categoriesArray.length > 0 && categoriesArray[0].movies.length > 0) {
          setFeaturedMovie(categoriesArray[0].movies[0]);
        }
      }
    } catch (error) {
      console.error('Error loading categories:', error);
      toast({
        title: "Error",
        description: "Failed to load movie categories. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async (query) => {
    if (!query.trim()) {
      setSearchResults([]);
      setIsSearching(false);
      return;
    }

    try {
      setIsSearching(true);
      const data = await moviesAPI.search(query);
      setSearchResults(data.results || []);
    } catch (error) {
      console.error('Error searching movies:', error);
      toast({
        title: "Search Error",
        description: "Failed to search movies. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSearching(false);
    }
  };

  const handlePlayMovie = (movie) => {
    if (movie.trailer_url) {
      window.open(movie.trailer_url, '_blank');
    } else {
      toast({
        title: "Playing " + movie.title,
        description: "Trailer not available for this title.",
      });
    }
  };

  const handleAddToList = async (movie) => {
    if (!isAuthenticated) {
      setAuthModalOpen(true);
      return;
    }

    try {
      await moviesAPI.addToWatchlist(movie.tmdb_id);
      toast({
        title: "Added to My List",
        description: `${movie.title} has been added to your watchlist.`,
      });
    } catch (error) {
      console.error('Error adding to watchlist:', error);
      toast({
        title: "Error",
        description: "Failed to add movie to watchlist.",
        variant: "destructive",
      });
    }
  };

  const MovieCard = ({ movie, size = 'md' }) => {
    const cardSizes = {
      sm: 'w-40 h-24',
      md: 'w-48 h-72',
      lg: 'w-56 h-80'
    };

    return (
      <div className={`${cardSizes[size]} flex-shrink-0 group cursor-pointer relative`}>
        <img
          src={movie.poster_url || 'https://via.placeholder.com/300x450?text=No+Image'}
          alt={movie.title}
          className="w-full h-full object-cover rounded-md transition-transform duration-300 group-hover:scale-105"
          onError={(e) => {
            e.target.src = 'https://via.placeholder.com/300x450?text=No+Image';
          }}
        />
        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-60 transition-all duration-300 rounded-md flex items-center justify-center">
          <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col items-center space-y-2">
            <Button
              size="sm"
              className="bg-white text-black hover:bg-gray-200"
              onClick={() => handlePlayMovie(movie)}
            >
              <Play className="w-4 h-4 mr-1" />
              Play
            </Button>
            <div className="flex space-x-2">
              <Button
                size="sm"
                variant="outline"
                className="border-gray-400 text-white hover:border-white"
                onClick={() => handleAddToList(movie)}
              >
                <Plus className="w-4 h-4" />
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="border-gray-400 text-white hover:border-white"
              >
                <ThumbsUp className="w-4 h-4" />
              </Button>
              <Dialog>
                <DialogTrigger asChild>
                  <Button
                    size="sm"
                    variant="outline"
                    className="border-gray-400 text-white hover:border-white"
                    onClick={() => setSelectedMovie(movie)}
                  >
                    <Info className="w-4 h-4" />
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-gray-900 text-white border-gray-700 max-w-2xl">
                  <DialogHeader>
                    <DialogTitle>{movie.title}</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4">
                    <img
                      src={movie.backdrop_url || movie.poster_url || 'https://via.placeholder.com/800x450?text=No+Image'}
                      alt={movie.title}
                      className="w-full h-48 object-cover rounded-md"
                      onError={(e) => {
                        e.target.src = 'https://via.placeholder.com/800x450?text=No+Image';
                      }}
                    />
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className="text-green-400 border-green-400">
                        {movie.rating}% Match
                      </Badge>
                      <span className="text-gray-400">{movie.year}</span>
                      {movie.genre && movie.genre.length > 0 && (
                        <Badge variant="secondary">{movie.genre[0]}</Badge>
                      )}
                      <Badge variant="outline" className="capitalize">
                        {movie.type}
                      </Badge>
                    </div>
                    <p className="text-gray-300">{movie.description}</p>
                    <div className="flex space-x-2">
                      <Button 
                        className="bg-red-600 hover:bg-red-700" 
                        onClick={() => handlePlayMovie(movie)}
                      >
                        <Play className="w-4 h-4 mr-2" />
                        {movie.trailer_url ? 'Play Trailer' : 'Play'}
                      </Button>
                      <Button 
                        variant="outline" 
                        className="border-gray-600 text-white hover:border-white" 
                        onClick={() => handleAddToList(movie)}
                      >
                        <Plus className="w-4 h-4 mr-2" />
                        My List
                      </Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </div>
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-2">
          <h4 className="text-white text-sm font-medium truncate">{movie.title}</h4>
        </div>
      </div>
    );
  };

  const MovieRow = ({ category, movies }) => {
    const [scrollPosition, setScrollPosition] = useState(0);
    const containerRef = React.useRef(null);

    const scroll = (direction) => {
      const container = containerRef.current;
      const scrollAmount = 300;
      const newPosition = direction === 'left' 
        ? Math.max(0, scrollPosition - scrollAmount)
        : scrollPosition + scrollAmount;
      
      container.scrollTo({ left: newPosition, behavior: 'smooth' });
      setScrollPosition(newPosition);
    };

    return (
      <div className="mb-8">
        <h2 className="text-white text-xl font-semibold mb-4 px-4">{category}</h2>
        <div className="relative group">
          <div 
            ref={containerRef}
            className="flex space-x-4 px-4 overflow-x-auto scrollbar-hide"
            style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
          >
            {movies && movies.length > 0 ? movies.map((movie, index) => (
              <MovieCard key={`${movie.tmdb_id || movie.id}-${index}`} movie={movie} />
            )) : (
              <div className="text-gray-400 px-4">No movies available</div>
            )}
          </div>
          {movies && movies.length > 5 && (
            <>
              <Button
                className="absolute left-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 hover:bg-opacity-70 opacity-0 group-hover:opacity-100 transition-opacity"
                size="sm"
                onClick={() => scroll('left')}
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <Button
                className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 hover:bg-opacity-70 opacity-0 group-hover:opacity-100 transition-opacity"
                size="sm"
                onClick={() => scroll('right')}
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
            </>
          )}
        </div>
      </div>
    );
  };

  // Show loading spinner while loading initial content
  if (isLoading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading Netflix content...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Navigation Header */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-black bg-opacity-90 backdrop-blur-sm transition-all duration-300">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center space-x-8">
            <h1 className="text-red-600 text-2xl font-bold">NETFLIX</h1>
            <div className="hidden md:flex space-x-6">
              <a href="#" className="text-white hover:text-gray-300 transition-colors">Home</a>
              <a href="#" className="text-white hover:text-gray-300 transition-colors">TV Shows</a>
              <a href="#" className="text-white hover:text-gray-300 transition-colors">Movies</a>
              <a href="#" className="text-white hover:text-gray-300 transition-colors">New & Popular</a>
              <a href="#" className="text-white hover:text-gray-300 transition-colors">My List</a>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <Input
                type="text"
                placeholder="Search movies and shows..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  handleSearch(e.target.value);
                }}
                className="bg-gray-800 border-gray-700 text-white pl-10 w-64"
              />
            </div>
            <Bell className="w-6 h-6 text-white cursor-pointer hover:text-gray-300" />
            
            {isAuthenticated ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <div className="w-8 h-8 bg-red-600 rounded-sm flex items-center justify-center cursor-pointer hover:bg-red-700 transition-colors">
                    <User className="w-5 h-5 text-white" />
                  </div>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="bg-gray-900 text-white border-gray-700">
                  <DropdownMenuItem className="hover:bg-gray-800">
                    {user?.username || 'Profile'}
                  </DropdownMenuItem>
                  <DropdownMenuItem 
                    className="hover:bg-gray-800 cursor-pointer"
                    onClick={logout}
                  >
                    <LogOut className="w-4 h-4 mr-2" />
                    Sign Out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <Button
                variant="outline"
                size="sm"
                className="border-red-600 text-red-600 hover:bg-red-600 hover:text-white"
                onClick={() => setAuthModalOpen(true)}
              >
                Sign In
              </Button>
            )}
          </div>
        </div>
      </nav>

      {/* Search Results */}
      {searchQuery && (
        <section className="pt-24 px-6">
          <h2 className="text-2xl font-bold mb-6">Search Results for "{searchQuery}"</h2>
          {isSearching ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-6 h-6 animate-spin mr-2" />
              <span>Searching...</span>
            </div>
          ) : searchResults.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {searchResults.map((movie, index) => (
                <MovieCard key={`${movie.tmdb_id}-${index}`} movie={movie} size="md" />
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-400">No results found for "{searchQuery}"</p>
            </div>
          )}
        </section>
      )}

      {/* Hero Section */}
      {!searchQuery && featuredMovie && (
        <section className="relative h-screen flex items-center">
          <div className="absolute inset-0">
            <img
              src={featuredMovie.backdrop_url || featuredMovie.poster_url || 'https://via.placeholder.com/1920x1080?text=No+Image'}
              alt={featuredMovie.title}
              className="w-full h-full object-cover"
              onError={(e) => {
                e.target.src = 'https://via.placeholder.com/1920x1080?text=No+Image';
              }}
            />
            <div className="absolute inset-0 bg-gradient-to-r from-black via-transparent to-transparent" />
            <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent" />
          </div>
          <div className="relative z-10 px-6 max-w-2xl ml-8">
            <h1 className="text-5xl md:text-7xl font-bold mb-4">{featuredMovie.title}</h1>
            <p className="text-lg md:text-xl mb-6 leading-relaxed">{featuredMovie.description}</p>
            <div className="flex items-center space-x-4 mb-6">
              <Badge variant="outline" className="text-green-400 border-green-400">
                {featuredMovie.rating}% Match
              </Badge>
              <span className="text-gray-300">{featuredMovie.year}</span>
              {featuredMovie.genre && featuredMovie.genre.length > 0 && (
                <Badge variant="secondary">{featuredMovie.genre[0]}</Badge>
              )}
            </div>
            <div className="flex space-x-4">
              <Button 
                size="lg" 
                className="bg-white text-black hover:bg-gray-200 px-8"
                onClick={() => handlePlayMovie(featuredMovie)}
              >
                <Play className="w-5 h-5 mr-2 fill-current" />
                {featuredMovie.trailer_url ? 'Play Trailer' : 'Play'}
              </Button>
              <Button 
                size="lg" 
                variant="outline" 
                className="border-gray-500 text-white hover:border-white bg-gray-800 bg-opacity-50 px-8"
                onClick={() => setSelectedMovie(featuredMovie)}
              >
                <Info className="w-5 h-5 mr-2" />
                More Info
              </Button>
            </div>
          </div>
        </section>
      )}

      {/* Movie Rows */}
      {!searchQuery && (
        <section className="relative z-10 -mt-32">
          {movieCategories.map((category, index) => (
            <MovieRow 
              key={index} 
              category={category.name} 
              movies={category.movies} 
            />
          ))}
        </section>
      )}

      {/* Auth Modal */}
      <AuthModal 
        isOpen={authModalOpen} 
        onClose={() => setAuthModalOpen(false)} 
      />
    </div>
  );
};

export default NetflixHome;