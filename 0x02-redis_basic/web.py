#!/usr/bin/env python3
"""Redis Module"""

from functools import wraps
import redis
import requests
from typing import Callable

# Connect to Redis
try:
    redis_ = redis.Redis()
    redis_.ping()  # Test connection
except redis.ConnectionError:
    print("Could not connect to Redis. Make sure the Redis server is running.")
    raise

def count_requests(method: Callable) -> Callable:
    """Decorator for counting requests and caching HTML."""
    @wraps(method)
    def wrapper(url: str) -> str:
        """Wrapper function for the decorator."""
        redis_.incr(f"count:{url}")
        cached_html = redis_.get(f"cached:{url}")
        if cached_html:
            return cached_html.decode('utf-8')
        
        try:
            html = method(url)
            redis_.setex(f"cached:{url}", 10, html)
            return html
        except requests.RequestException as e:
            return f"Error fetching the page: {e}"

    return wrapper

@count_requests
def get_page(url: str) -> str:
    """Obtain the HTML content of a URL."""
    req = requests.get(url, timeout=5)  # Add timeout to handle slow responses
    req.raise_for_status()  # Raise an exception for HTTP errors
    return req.text

# Example usage
if __name__ == "__main__":
    url = "http://slowwly.robertomurray.co.uk/delay/5000/url/https://www.google.com"
    print(get_page(url))

