import React, { useState, useEffect } from 'react';
import { Play, Info, Search, Bell, User, ChevronLeft, ChevronRight, Plus, ThumbsUp, ThumbsDown } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Badge } from './ui/badge';
import { useToast } from '../hooks/use-toast';
import { mockMovieData } from '../data/mockData';

const NetflixHome = () => {
  const [featuredMovie, setFeaturedMovie] = useState(null);
  const [movieCategories, setMovieCategories] = useState([]);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    // Set featured movie and categories from mock data
    const categories = mockMovieData.categories;
    setMovieCategories(categories);
    if (categories.length > 0 && categories[0].movies.length > 0) {
      setFeaturedMovie(categories[0].movies[0]);
    }
  }, []);

  const handlePlayMovie = (movie) => {
    toast({
      title: "Playing " + movie.title,
      description: "Opening video player...",
    });
    // In a real app, this would open the video player
  };

  const handleAddToList = (movie) => {
    toast({
      title: "Added to My List",
      description: `${movie.title} has been added to your watchlist.`,
    });
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
          src={movie.poster}
          alt={movie.title}
          className="w-full h-full object-cover rounded-md transition-transform duration-300 group-hover:scale-105"
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
                <DialogContent className="bg-gray-900 text-white border-gray-700">
                  <DialogHeader>
                    <DialogTitle>{movie.title}</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4">
                    <img
                      src={movie.backdrop}
                      alt={movie.title}
                      className="w-full h-48 object-cover rounded-md"
                    />
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className="text-green-400 border-green-400">
                        {movie.rating}% Match
                      </Badge>
                      <span className="text-gray-400">{movie.year}</span>
                      <Badge variant="secondary">{movie.genre}</Badge>
                    </div>
                    <p className="text-gray-300">{movie.description}</p>
                    <div className="flex space-x-2">
                      <Button className="bg-red-600 hover:bg-red-700" onClick={() => handlePlayMovie(movie)}>
                        <Play className="w-4 h-4 mr-2" />
                        Play
                      </Button>
                      <Button variant="outline" className="border-gray-600 text-white hover:border-white" onClick={() => handleAddToList(movie)}>
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
            {movies.map((movie, index) => (
              <MovieCard key={index} movie={movie} />
            ))}
          </div>
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
        </div>
      </div>
    );
  };

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
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-gray-800 border-gray-700 text-white pl-10 w-64"
              />
            </div>
            <Bell className="w-6 h-6 text-white cursor-pointer hover:text-gray-300" />
            <div className="w-8 h-8 bg-red-600 rounded-sm flex items-center justify-center cursor-pointer">
              <User className="w-5 h-5 text-white" />
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      {featuredMovie && (
        <section className="relative h-screen flex items-center">
          <div className="absolute inset-0">
            <img
              src={featuredMovie.backdrop}
              alt={featuredMovie.title}
              className="w-full h-full object-cover"
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
              <Badge variant="secondary">{featuredMovie.genre}</Badge>
            </div>
            <div className="flex space-x-4">
              <Button 
                size="lg" 
                className="bg-white text-black hover:bg-gray-200 px-8"
                onClick={() => handlePlayMovie(featuredMovie)}
              >
                <Play className="w-5 h-5 mr-2 fill-current" />
                Play
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
      <section className="relative z-10 -mt-32">
        {movieCategories.map((category, index) => (
          <MovieRow 
            key={index} 
            category={category.name} 
            movies={category.movies} 
          />
        ))}
      </section>
    </div>
  );
};

export default NetflixHome;