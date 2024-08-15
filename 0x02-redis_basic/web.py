#!/usr/bin/env python3
"""
Web cache and tracker
"""
import requests
import redis
from functools import wraps
from typing import Callable

store = redis.Redis()

def count_url_access(method: Callable) -> Callable:
    """ Decorator counting how many times a URL is accessed """
    @wraps(method)
    def wrapper(url: str) -> str:
        store.incr(f"count:{url}")
        cached_key = f"cached:{url}"
        cached_data = store.get(cached_key)
        if cached_data:
            return cached_data.decode("utf-8")
        html = method(url)
        store.setex(cached_key, 10, html)
        return html
    return wrapper

@count_url_access
def get_page(url: str) -> str:
    """ Returns HTML content of a url """
    res = requests.get(url)
    return res.text

if __name__ == "__main__":
    get_page('http://slowwly.robertomurray.co.uk')
