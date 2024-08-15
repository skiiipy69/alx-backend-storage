#!/usr/bin/env python3
""" Redis-based web cache and tracker """

import redis
import requests
from typing import Callable
from functools import wraps

# Set up a connection to the local Redis server
redis_client = redis.Redis()

def count_requests(method: Callable) -> Callable:
    """Decorator to count and cache the number of requests to a URL."""
    @wraps(method)
    def wrapper(url: str) -> str:
        # Increment the access count for the URL
        redis_client.incr(f"count:{url}")
        
        # Try to retrieve the cached HTML content
        cached_html = redis_client.get(f"cached:{url}")
        if cached_html:
            return cached_html.decode('utf-8')
        
        # Fetch the content from the URL and cache it with a 10-second expiration
        html = method(url)
        redis_client.setex(f"cached:{url}", 10, html)
        return html

    return wrapper

@count_requests
def get_page(url: str) -> str:
    """Fetches the HTML content of a URL."""
    response = requests.get(url)
    return response.text

# Example usage
if __name__ == "__main__":
    # Use a slow response URL to test the caching functionality
    slow_url = "http://slowwly.robertomurray.co.uk/delay/5000/url/http://www.google.com"
    
    # Fetch the page (the first time it should take longer, subsequent times should be faster)
    print(get_page(slow_url))
    print(f"Count for {slow_url}: {redis_client.get(f'count:{slow_url}').decode('utf-8')}")

    # Wait for more than 10 seconds to allow the cache to expire, then fetch again
    import time
    time.sleep(11)
    print(get_page(slow_url))
    print(f"Count for {slow_url}: {redis_client.get(f'count:{slow_url}').decode('utf-8')}")

