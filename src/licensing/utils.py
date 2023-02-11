import logging

from functools import wraps
import time


def async_measure_time(func):
    @wraps(func)
    async def measure_time_wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        logging.info(f"Function {func.__name__}{args} {kwargs} took {round((time.time() - start) * 1000)} msecs")
        return result
    return measure_time_wrapper
