import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login if needed
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_data');
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: async (userData) => {
    const response = await apiClient.post('/auth/register', userData);
    return response.data;
  },

  login: async (credentials) => {
    const response = await apiClient.post('/auth/login', credentials);
    return response.data;
  },

  getProfile: async () => {
    const response = await apiClient.get('/auth/profile');
    return response.data;
  },
};

// Movies API
export const moviesAPI = {
  getCategories: async () => {
    const response = await apiClient.get('/movies/categories');
    return response.data;
  },

  getTrending: async () => {
    const response = await apiClient.get('/movies/trending');
    return response.data;
  },

  getPopular: async () => {
    const response = await apiClient.get('/movies/popular');
    return response.data;
  },

  search: async (query) => {
    const response = await apiClient.get(`/movies/search?q=${encodeURIComponent(query)}`);
    return response.data;
  },

  getDetails: async (movieId, mediaType = 'movie') => {
    const response = await apiClient.get(`/movies/${movieId}?media_type=${mediaType}`);
    return response.data;
  },

  addToWatchlist: async (movieId) => {
    const response = await apiClient.post(`/movies/${movieId}/watchlist`);
    return response.data;
  },

  removeFromWatchlist: async (movieId) => {
    const response = await apiClient.delete(`/movies/${movieId}/watchlist`);
    return response.data;
  },

  getWatchlist: async () => {
    const response = await apiClient.get('/users/watchlist');
    return response.data;
  },
};

export default apiClient;