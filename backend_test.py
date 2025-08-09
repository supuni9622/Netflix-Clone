#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Netflix Clone
Tests TMDB integration, authentication, watchlist functionality, and error handling
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NetflixCloneAPITester:
    def __init__(self):
        # Get backend URL from frontend .env file
        self.base_url = self._get_backend_url()
        self.session = None
        self.test_user_token = None
        self.test_user_data = {
            "username": "netflix_tester",
            "email": "tester@netflix.com",
            "password": "TestPassword123!"
        }
        self.test_results = {
            "tmdb_integration": {},
            "authentication": {},
            "watchlist": {},
            "error_handling": {},
            "database": {}
        }
        
    def _get_backend_url(self) -> str:
        """Get backend URL from frontend .env file"""
        try:
            with open('/app/frontend/.env', 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        backend_url = line.split('=', 1)[1].strip()
                        return f"{backend_url}/api"
        except Exception as e:
            logger.error(f"Could not read backend URL from frontend/.env: {e}")
        
        # Fallback
        return "http://localhost:8001/api"
    
    async def setup_session(self):
        """Setup aiohttp session"""
        self.session = aiohttp.ClientSession()
        logger.info(f"Testing backend at: {self.base_url}")
    
    async def cleanup_session(self):
        """Cleanup aiohttp session"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None, 
                          headers: Dict = None, params: Dict = None) -> Dict[str, Any]:
        """Make HTTP request and return response data"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(
                method, url, json=data, headers=headers, params=params
            ) as response:
                response_data = {
                    "status": response.status,
                    "headers": dict(response.headers),
                    "data": None
                }
                
                try:
                    response_data["data"] = await response.json()
                except:
                    response_data["data"] = await response.text()
                
                return response_data
        except Exception as e:
            logger.error(f"Request failed for {method} {url}: {e}")
            return {"status": 0, "error": str(e), "data": None}
    
    # TMDB Integration Tests
    async def test_tmdb_categories(self):
        """Test /api/movies/categories endpoint"""
        logger.info("Testing TMDB categories endpoint...")
        
        response = await self.make_request("GET", "/movies/categories")
        
        if response["status"] == 200:
            data = response["data"]
            if "categories" in data and isinstance(data["categories"], dict):
                categories = data["categories"]
                
                # Check if we have expected categories
                expected_categories = ["Trending Now", "Popular Movies", "Popular TV Shows", "Action & Adventure", "Comedy"]
                found_categories = list(categories.keys())
                
                # Verify each category has movies
                valid_categories = 0
                for cat_name, movies in categories.items():
                    if isinstance(movies, list) and len(movies) > 0:
                        # Check first movie structure
                        if movies and self._validate_movie_structure(movies[0]):
                            valid_categories += 1
                
                self.test_results["tmdb_integration"]["categories"] = {
                    "status": "PASS",
                    "categories_found": len(found_categories),
                    "valid_categories": valid_categories,
                    "sample_categories": found_categories[:3]
                }
                logger.info(f"✅ Categories test passed - Found {len(found_categories)} categories")
            else:
                self.test_results["tmdb_integration"]["categories"] = {
                    "status": "FAIL",
                    "error": "Invalid response structure"
                }
                logger.error("❌ Categories test failed - Invalid response structure")
        else:
            self.test_results["tmdb_integration"]["categories"] = {
                "status": "FAIL",
                "error": f"HTTP {response['status']}: {response.get('data', 'Unknown error')}"
            }
            logger.error(f"❌ Categories test failed - HTTP {response['status']}")
    
    async def test_tmdb_trending(self):
        """Test /api/movies/trending endpoint"""
        logger.info("Testing TMDB trending endpoint...")
        
        response = await self.make_request("GET", "/movies/trending")
        
        if response["status"] == 200:
            data = response["data"]
            if "movies" in data and isinstance(data["movies"], list) and len(data["movies"]) > 0:
                movies = data["movies"]
                valid_movies = sum(1 for movie in movies if self._validate_movie_structure(movie))
                
                self.test_results["tmdb_integration"]["trending"] = {
                    "status": "PASS",
                    "total_movies": len(movies),
                    "valid_movies": valid_movies,
                    "sample_movie": movies[0] if movies else None
                }
                logger.info(f"✅ Trending test passed - Found {len(movies)} movies")
            else:
                self.test_results["tmdb_integration"]["trending"] = {
                    "status": "FAIL",
                    "error": "No movies found or invalid structure"
                }
                logger.error("❌ Trending test failed - No movies found")
        else:
            self.test_results["tmdb_integration"]["trending"] = {
                "status": "FAIL",
                "error": f"HTTP {response['status']}: {response.get('data', 'Unknown error')}"
            }
            logger.error(f"❌ Trending test failed - HTTP {response['status']}")
    
    async def test_tmdb_popular(self):
        """Test /api/movies/popular endpoint"""
        logger.info("Testing TMDB popular endpoint...")
        
        response = await self.make_request("GET", "/movies/popular")
        
        if response["status"] == 200:
            data = response["data"]
            if "movies" in data and isinstance(data["movies"], list) and len(data["movies"]) > 0:
                movies = data["movies"]
                valid_movies = sum(1 for movie in movies if self._validate_movie_structure(movie))
                
                self.test_results["tmdb_integration"]["popular"] = {
                    "status": "PASS",
                    "total_movies": len(movies),
                    "valid_movies": valid_movies
                }
                logger.info(f"✅ Popular test passed - Found {len(movies)} movies")
            else:
                self.test_results["tmdb_integration"]["popular"] = {
                    "status": "FAIL",
                    "error": "No movies found or invalid structure"
                }
                logger.error("❌ Popular test failed - No movies found")
        else:
            self.test_results["tmdb_integration"]["popular"] = {
                "status": "FAIL",
                "error": f"HTTP {response['status']}: {response.get('data', 'Unknown error')}"
            }
            logger.error(f"❌ Popular test failed - HTTP {response['status']}")
    
    async def test_tmdb_search(self):
        """Test /api/movies/search endpoint with different queries"""
        logger.info("Testing TMDB search endpoint...")
        
        search_queries = ["avengers", "stranger things", "batman"]
        search_results = {}
        
        for query in search_queries:
            response = await self.make_request("GET", "/movies/search", params={"q": query})
            
            if response["status"] == 200:
                data = response["data"]
                if "results" in data and isinstance(data["results"], list):
                    results = data["results"]
                    valid_results = sum(1 for movie in results if self._validate_movie_structure(movie))
                    search_results[query] = {
                        "status": "PASS",
                        "total_results": len(results),
                        "valid_results": valid_results
                    }
                    logger.info(f"✅ Search for '{query}' passed - Found {len(results)} results")
                else:
                    search_results[query] = {
                        "status": "FAIL",
                        "error": "Invalid response structure"
                    }
                    logger.error(f"❌ Search for '{query}' failed - Invalid structure")
            else:
                search_results[query] = {
                    "status": "FAIL",
                    "error": f"HTTP {response['status']}: {response.get('data', 'Unknown error')}"
                }
                logger.error(f"❌ Search for '{query}' failed - HTTP {response['status']}")
        
        # Check if all searches passed
        all_passed = all(result.get("status") == "PASS" for result in search_results.values())
        self.test_results["tmdb_integration"]["search"] = {
            "status": "PASS" if all_passed else "FAIL",
            "individual_results": search_results
        }
    
    async def test_tmdb_movie_details(self):
        """Test /api/movies/{movie_id} endpoint"""
        logger.info("Testing TMDB movie details endpoint...")
        
        # First get a movie ID from trending
        trending_response = await self.make_request("GET", "/movies/trending")
        
        if trending_response["status"] == 200 and "movies" in trending_response["data"]:
            movies = trending_response["data"]["movies"]
            if movies:
                test_movie = movies[0]
                movie_id = test_movie.get("tmdb_id")
                media_type = test_movie.get("type", "movie")
                
                if movie_id:
                    response = await self.make_request("GET", f"/movies/{movie_id}", 
                                                     params={"media_type": media_type})
                    
                    if response["status"] == 200:
                        movie_data = response["data"]
                        if self._validate_movie_structure(movie_data, detailed=True):
                            self.test_results["tmdb_integration"]["movie_details"] = {
                                "status": "PASS",
                                "movie_id": movie_id,
                                "has_trailer": bool(movie_data.get("trailer_url"))
                            }
                            logger.info(f"✅ Movie details test passed for ID {movie_id}")
                        else:
                            self.test_results["tmdb_integration"]["movie_details"] = {
                                "status": "FAIL",
                                "error": "Invalid movie structure"
                            }
                            logger.error("❌ Movie details test failed - Invalid structure")
                    else:
                        self.test_results["tmdb_integration"]["movie_details"] = {
                            "status": "FAIL",
                            "error": f"HTTP {response['status']}: {response.get('data', 'Unknown error')}"
                        }
                        logger.error(f"❌ Movie details test failed - HTTP {response['status']}")
                else:
                    self.test_results["tmdb_integration"]["movie_details"] = {
                        "status": "FAIL",
                        "error": "No movie ID found in trending movies"
                    }
                    logger.error("❌ Movie details test failed - No movie ID")
            else:
                self.test_results["tmdb_integration"]["movie_details"] = {
                    "status": "FAIL",
                    "error": "No trending movies found"
                }
                logger.error("❌ Movie details test failed - No trending movies")
        else:
            self.test_results["tmdb_integration"]["movie_details"] = {
                "status": "FAIL",
                "error": "Could not fetch trending movies"
            }
            logger.error("❌ Movie details test failed - Could not fetch trending movies")
    
    # Authentication Tests
    async def test_user_registration(self):
        """Test user registration"""
        logger.info("Testing user registration...")
        
        response = await self.make_request("POST", "/auth/register", data=self.test_user_data)
        
        if response["status"] == 200:
            data = response["data"]
            if "access_token" in data and "user" in data:
                self.test_user_token = data["access_token"]
                user_data = data["user"]
                
                # Validate user structure
                required_fields = ["id", "username", "email", "watchlist", "created_at"]
                if all(field in user_data for field in required_fields):
                    self.test_results["authentication"]["registration"] = {
                        "status": "PASS",
                        "user_id": user_data["id"],
                        "token_received": bool(self.test_user_token)
                    }
                    logger.info("✅ User registration test passed")
                else:
                    self.test_results["authentication"]["registration"] = {
                        "status": "FAIL",
                        "error": "Invalid user data structure"
                    }
                    logger.error("❌ User registration test failed - Invalid user structure")
            else:
                self.test_results["authentication"]["registration"] = {
                    "status": "FAIL",
                    "error": "Missing access_token or user data"
                }
                logger.error("❌ User registration test failed - Missing token/user")
        elif response["status"] == 400:
            # User might already exist, try login instead
            logger.info("User already exists, testing login...")
            await self.test_user_login()
        else:
            self.test_results["authentication"]["registration"] = {
                "status": "FAIL",
                "error": f"HTTP {response['status']}: {response.get('data', 'Unknown error')}"
            }
            logger.error(f"❌ User registration test failed - HTTP {response['status']}")
    
    async def test_user_login(self):
        """Test user login"""
        logger.info("Testing user login...")
        
        login_data = {
            "email": self.test_user_data["email"],
            "password": self.test_user_data["password"]
        }
        
        response = await self.make_request("POST", "/auth/login", data=login_data)
        
        if response["status"] == 200:
            data = response["data"]
            if "access_token" in data and "user" in data:
                self.test_user_token = data["access_token"]
                
                self.test_results["authentication"]["login"] = {
                    "status": "PASS",
                    "token_received": bool(self.test_user_token)
                }
                logger.info("✅ User login test passed")
            else:
                self.test_results["authentication"]["login"] = {
                    "status": "FAIL",
                    "error": "Missing access_token or user data"
                }
                logger.error("❌ User login test failed - Missing token/user")
        else:
            self.test_results["authentication"]["login"] = {
                "status": "FAIL",
                "error": f"HTTP {response['status']}: {response.get('data', 'Unknown error')}"
            }
            logger.error(f"❌ User login test failed - HTTP {response['status']}")
    
    async def test_protected_profile_access(self):
        """Test accessing protected profile endpoint"""
        logger.info("Testing protected profile access...")
        
        if not self.test_user_token:
            self.test_results["authentication"]["profile_access"] = {
                "status": "FAIL",
                "error": "No authentication token available"
            }
            logger.error("❌ Profile access test failed - No token")
            return
        
        headers = {"Authorization": f"Bearer {self.test_user_token}"}
        response = await self.make_request("GET", "/auth/profile", headers=headers)
        
        if response["status"] == 200:
            profile_data = response["data"]
            required_fields = ["id", "username", "email", "watchlist", "created_at"]
            
            if all(field in profile_data for field in required_fields):
                self.test_results["authentication"]["profile_access"] = {
                    "status": "PASS",
                    "profile_data": profile_data
                }
                logger.info("✅ Profile access test passed")
            else:
                self.test_results["authentication"]["profile_access"] = {
                    "status": "FAIL",
                    "error": "Invalid profile data structure"
                }
                logger.error("❌ Profile access test failed - Invalid structure")
        else:
            self.test_results["authentication"]["profile_access"] = {
                "status": "FAIL",
                "error": f"HTTP {response['status']}: {response.get('data', 'Unknown error')}"
            }
            logger.error(f"❌ Profile access test failed - HTTP {response['status']}")
    
    # Watchlist Tests
    async def test_watchlist_functionality(self):
        """Test complete watchlist functionality"""
        logger.info("Testing watchlist functionality...")
        
        if not self.test_user_token:
            self.test_results["watchlist"]["functionality"] = {
                "status": "FAIL",
                "error": "No authentication token available"
            }
            logger.error("❌ Watchlist test failed - No token")
            return
        
        # Get a movie ID to test with
        trending_response = await self.make_request("GET", "/movies/trending")
        if trending_response["status"] != 200 or not trending_response["data"].get("movies"):
            self.test_results["watchlist"]["functionality"] = {
                "status": "FAIL",
                "error": "Could not get test movie"
            }
            logger.error("❌ Watchlist test failed - No test movie")
            return
        
        test_movie_id = trending_response["data"]["movies"][0]["tmdb_id"]
        headers = {"Authorization": f"Bearer {self.test_user_token}"}
        
        # Test adding to watchlist
        add_response = await self.make_request("POST", f"/movies/{test_movie_id}/watchlist", headers=headers)
        
        if add_response["status"] == 200:
            logger.info(f"✅ Added movie {test_movie_id} to watchlist")
            
            # Test getting watchlist
            watchlist_response = await self.make_request("GET", "/users/watchlist", headers=headers)
            
            if watchlist_response["status"] == 200:
                watchlist_data = watchlist_response["data"]
                if "watchlist" in watchlist_data and isinstance(watchlist_data["watchlist"], list):
                    watchlist = watchlist_data["watchlist"]
                    movie_found = any(movie.get("tmdb_id") == test_movie_id for movie in watchlist)
                    
                    if movie_found:
                        logger.info("✅ Movie found in watchlist")
                        
                        # Test removing from watchlist
                        remove_response = await self.make_request("DELETE", f"/movies/{test_movie_id}/watchlist", headers=headers)
                        
                        if remove_response["status"] == 200:
                            logger.info(f"✅ Removed movie {test_movie_id} from watchlist")
                            
                            self.test_results["watchlist"]["functionality"] = {
                                "status": "PASS",
                                "test_movie_id": test_movie_id,
                                "add_success": True,
                                "retrieve_success": True,
                                "remove_success": True
                            }
                        else:
                            self.test_results["watchlist"]["functionality"] = {
                                "status": "FAIL",
                                "error": f"Failed to remove from watchlist: HTTP {remove_response['status']}"
                            }
                            logger.error("❌ Failed to remove from watchlist")
                    else:
                        self.test_results["watchlist"]["functionality"] = {
                            "status": "FAIL",
                            "error": "Movie not found in watchlist after adding"
                        }
                        logger.error("❌ Movie not found in watchlist")
                else:
                    self.test_results["watchlist"]["functionality"] = {
                        "status": "FAIL",
                        "error": "Invalid watchlist response structure"
                    }
                    logger.error("❌ Invalid watchlist structure")
            else:
                self.test_results["watchlist"]["functionality"] = {
                    "status": "FAIL",
                    "error": f"Failed to get watchlist: HTTP {watchlist_response['status']}"
                }
                logger.error("❌ Failed to get watchlist")
        else:
            self.test_results["watchlist"]["functionality"] = {
                "status": "FAIL",
                "error": f"Failed to add to watchlist: HTTP {add_response['status']}"
            }
            logger.error("❌ Failed to add to watchlist")
    
    # Error Handling Tests
    async def test_error_handling(self):
        """Test various error scenarios"""
        logger.info("Testing error handling...")
        
        # Test 404 for invalid endpoints
        response_404 = await self.make_request("GET", "/invalid/endpoint")
        
        # Test 401 for unauthorized access
        response_401 = await self.make_request("GET", "/auth/profile")
        
        # Test invalid movie ID
        response_invalid_movie = await self.make_request("GET", "/movies/999999999")
        
        # Test empty search query
        response_empty_search = await self.make_request("GET", "/movies/search", params={"q": ""})
        
        self.test_results["error_handling"] = {
            "invalid_endpoint": {
                "status": "PASS" if response_404["status"] == 404 else "FAIL",
                "response_code": response_404["status"]
            },
            "unauthorized_access": {
                "status": "PASS" if response_401["status"] == 401 else "FAIL",
                "response_code": response_401["status"]
            },
            "invalid_movie_id": {
                "status": "PASS" if response_invalid_movie["status"] in [404, 500] else "FAIL",
                "response_code": response_invalid_movie["status"]
            },
            "empty_search": {
                "status": "PASS" if response_empty_search["status"] == 400 else "FAIL",
                "response_code": response_empty_search["status"]
            }
        }
        
        logger.info("✅ Error handling tests completed")
    
    # Database Integration Test
    async def test_database_integration(self):
        """Test MongoDB connection and data persistence"""
        logger.info("Testing database integration...")
        
        # Test health check endpoint
        health_response = await self.make_request("GET", "/")
        
        if health_response["status"] == 200:
            self.test_results["database"]["health_check"] = {
                "status": "PASS",
                "response": health_response["data"]
            }
            logger.info("✅ Database health check passed")
        else:
            self.test_results["database"]["health_check"] = {
                "status": "FAIL",
                "error": f"HTTP {health_response['status']}"
            }
            logger.error("❌ Database health check failed")
        
        # Test user data persistence (if we have a token)
        if self.test_user_token:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            profile_response = await self.make_request("GET", "/auth/profile", headers=headers)
            
            if profile_response["status"] == 200:
                self.test_results["database"]["user_persistence"] = {
                    "status": "PASS",
                    "user_data_retrieved": True
                }
                logger.info("✅ User data persistence test passed")
            else:
                self.test_results["database"]["user_persistence"] = {
                    "status": "FAIL",
                    "error": "Could not retrieve user data"
                }
                logger.error("❌ User data persistence test failed")
    
    def _validate_movie_structure(self, movie: Dict, detailed: bool = False) -> bool:
        """Validate movie data structure"""
        required_fields = ["tmdb_id", "title", "description", "genre", "year", "rating", "poster_url", "backdrop_url", "type"]
        
        if detailed:
            # For detailed movie info, trailer_url should be present (can be None)
            required_fields.append("trailer_url")
        
        return all(field in movie for field in required_fields)
    
    async def run_all_tests(self):
        """Run all tests"""
        logger.info("🚀 Starting Netflix Clone Backend API Tests")
        logger.info("=" * 60)
        
        await self.setup_session()
        
        try:
            # TMDB Integration Tests
            logger.info("\n📡 TMDB INTEGRATION TESTS")
            logger.info("-" * 30)
            await self.test_tmdb_categories()
            await self.test_tmdb_trending()
            await self.test_tmdb_popular()
            await self.test_tmdb_search()
            await self.test_tmdb_movie_details()
            
            # Authentication Tests
            logger.info("\n🔐 AUTHENTICATION TESTS")
            logger.info("-" * 30)
            await self.test_user_registration()
            await self.test_protected_profile_access()
            
            # Watchlist Tests
            logger.info("\n📝 WATCHLIST TESTS")
            logger.info("-" * 30)
            await self.test_watchlist_functionality()
            
            # Error Handling Tests
            logger.info("\n⚠️  ERROR HANDLING TESTS")
            logger.info("-" * 30)
            await self.test_error_handling()
            
            # Database Tests
            logger.info("\n💾 DATABASE INTEGRATION TESTS")
            logger.info("-" * 30)
            await self.test_database_integration()
            
        finally:
            await self.cleanup_session()
        
        # Print summary
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        logger.info("\n" + "=" * 60)
        logger.info("🎬 NETFLIX CLONE BACKEND TEST SUMMARY")
        logger.info("=" * 60)
        
        total_tests = 0
        passed_tests = 0
        
        for category, tests in self.test_results.items():
            logger.info(f"\n📊 {category.upper().replace('_', ' ')} RESULTS:")
            logger.info("-" * 40)
            
            for test_name, result in tests.items():
                total_tests += 1
                status = result.get("status", "UNKNOWN")
                
                if status == "PASS":
                    passed_tests += 1
                    logger.info(f"  ✅ {test_name}: PASSED")
                else:
                    logger.info(f"  ❌ {test_name}: FAILED")
                    if "error" in result:
                        logger.info(f"     Error: {result['error']}")
        
        logger.info("\n" + "=" * 60)
        logger.info(f"📈 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            logger.info("🎉 ALL TESTS PASSED! Netflix Clone Backend is working correctly.")
        else:
            logger.info(f"⚠️  {total_tests - passed_tests} tests failed. Check logs for details.")
        
        logger.info("=" * 60)
        
        # Return results for programmatic access
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "detailed_results": self.test_results
        }

async def main():
    """Main test runner"""
    tester = NetflixCloneAPITester()
    results = await tester.run_all_tests()
    
    # Save results to file
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"\n📄 Detailed results saved to: /app/backend_test_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())