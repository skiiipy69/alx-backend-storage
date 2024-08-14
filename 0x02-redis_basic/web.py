#!/usr/bin/env python3
"""
Caching request module
"""
import redis
import requests
from functools import wraps
from typing import Callable

# Initialize the Redis client
client = redis.Redis()

def track_get_page(fn: Callable) -> Callable:
    """Decorator for get_page to track and cache page requests."""
    @wraps(fn)
    def wrapper(url: str) -> str:
        """Wrapper that:
        - Checks whether a URL's data is cached
        - Tracks how many times get_page is called
        """
        # Increment the access count for the URL
        client.incr(f'count:{url}')
        
        # Check if the page content is already cached
        cached_page = client.get(f'{url}')
        if cached_page:
            return cached_page.decode('utf-8')
        
        # If not cached, call the original function to get the page content
        response = fn(url)
        
        # Cache the page content with an expiration time of 10 seconds
        client.setex(f'{url}', 10, response)
        
        return response
    return wrapper

@track_get_page
def get_page(url: str) -> str:
    """Makes an HTTP request to a given URL and returns the content."""
    response = requests.get(url)
    return response.text

if __name__ == "__main__":
    # Example usage of get_page
    url = "http://slowwly.robertomurray.co.uk/delay/1000/url/http://www.example.com"
    print(get_page(url))
    # Access the URL multiple times to test the cache and tracking
    print(get_page(url))
