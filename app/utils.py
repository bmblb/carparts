import time
import random

def delay(timeout):
    '''Delays execution for timeout +- 5%'''
    def decorator(function):
        def wrapper(*args, **kwargs):
            time.sleep(random.randint(timeout * 95, timeout * 105) / 100)
            return function(*args, **kwargs)
        return wrapper
    return decorator
