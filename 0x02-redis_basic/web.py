#!/usr/bin/env python3
""" Redis Module """

from functools import wraps
import redis
import requests
from typing import Callable
import time

# Connect to Redis
try:
    redis_ = redis.Redis()
    redis_.ping()  # Check if the Redis server is running
    print("Connected to Redis successfully!")
except redis.ConnectionError as e:
    print(f"Redis connection error: {e}")
    exit(1)

def count_requests(method: Callable) -> Callable:
    """Decorator for counting and caching requests."""
    @wraps(method)
    def wrapper(url: str) -> str:
        """Wrapper for the decorator."""
        try:
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
        except Exception as e:
            print(f"Error in wrapper: {e}")
            return "Error"

    return wrapper

@count_requests
def get_page(url: str) -> str:
    """Obtain the HTML content of a URL."""
    try:
        req = requests.get(url)
        req.raise_for_status()  # Ensure that the request was successful
        return req.text
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return "Error"

# Example usage
if __name__ == "__main__":
    url = "http://google.com"
    
    print("First request:")
    page_content = get_page(url)
    print(page_content[:200] if len(page_content) > 200 else page_content)  # Print the first 200 chars
    
    print("\nChecking count and cache status:")
    try:
        count = redis_.get(f"count:{url}").decode('utf-8')
        cached_html = redis_.get(f"cached:{url}")
        print(f"Count: {count}")
        print(f"Cached HTML: {cached_html[:200].decode('utf-8') if cached_html else 'None'}")
    except Exception as e:
        print(f"Error accessing Redis: {e}")
    
    print("\nWaiting 11 seconds to check cache expiration...")
    time.sleep(11)
    
    print("\nSecond request (after cache expiration):")
    page_content = get_page(url)
    print(page_content[:200] if len(page_content) > 200 else page_content)  # Print the first 200 chars
    
    print("\nFinal count and cache status:")
    try:
        count = redis_.get(f"count:{url}").decode('utf-8')
        cached_html = redis_.get(f"cached:{url}")
        print(f"Count: {count}")
        print(f"Cached HTML: {cached_html[:200].decode('utf-8') if cached_html else 'None'}")
    except Exception as e:
        print(f"Error accessing Redis: {e}")

