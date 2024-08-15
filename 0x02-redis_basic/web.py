#!/usr/bin/env python3
'''A module with tools for request caching and tracking.
'''

import redis
import requests
from functools import wraps
from typing import Callable

# Update Redis connection to use port 6380
redis_store = redis.Redis(host='localhost', port=6380)
'''The module-level Redis instance.
'''

def data_cacher(method: Callable) -> Callable:
    '''Caches the output of fetched data.
    '''
    @wraps(method)
    def invoker(url: str) -> str:
        '''The wrapper function for caching the output.
        '''
        redis_store.incr(f'count:{url}')  # Increment access count
        result = redis_store.get(f'result:{url}')
        if result:
            return result.decode('utf-8')
        
        # Fetch data and cache it
        result = method(url)
        redis_store.setex(f'result:{url}', 10, result)
        return result
    
    return invoker

@data_cacher
def get_page(url: str) -> str:
    '''Returns the content of a URL after caching the request's response,
    and tracking the request.
    '''
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text
    except requests.RequestException as e:
        return str(e)

# Testing the function
if __name__ == "__main__":
    url = 'http://google.com'
    print(get_page(url))
    
    # Fetch and print the count of how many times the page was accessed
    count = redis_store.get(f'count:{url}')
    print(count.decode('utf-8') if count else '0')  # Handle case where count is None
