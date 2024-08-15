#!/usr/bin/env python3
""" Redis Module """

from functools import wraps
import redis
import requests
from typing import Callable
import time

redis_ = redis.Redis()

def count_requests(method: Callable) -> Callable:
    """Decorator for counting and caching requests."""
    @wraps(method)
    def wrapper(url: str) -> str:
        """Wrapper for the decorator."""
        # Increment the count for this URL
        redis_.incr(f"count:{url}")
        
        # Try to get cached content
        cached_html = redis_.get(f"cached:{url}")
        if cached_html:
            print("Cache hit!")
            return cached_html.decode('utf-8')

        # If not cached, fetch the content and cache it
        html = method(url)
        redis_.setex(f"cached:{url}", 10, html)
        print("Content cached for 10 seconds.")

        return html

    return wrapper

@count_requests
def get_page(url: str) -> str:
    """Obtain the HTML content of a URL."""
    req = requests.get(url)
    return req.text

# Example usage
if __name__ == "__main__":
    url = "http://google.com"
    
    print("First request:")
    print(get_page(url))
    
    print("\nChecking count and cache status:")
    print(f"Count: {redis_.get(f'count:{url}').decode('utf-8')}")
    print(f"Cached HTML: {redis_.get(f'cached:{url}')}")
    
    print("\nWaiting 11 seconds to check cache expiration...")
    time.sleep(11)
    
    print("\nSecond request (after cache expiration):")
    print(get_page(url))
    
    print("\nFinal count and cache status:")
    print(f"Count: {redis_.get(f'count:{url}').decode('utf-8')}")
    print(f"Cached HTML: {redis_.get(f'cached:{url}')}")

