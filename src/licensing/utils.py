import logging
import time
from functools import wraps


def async_measure_time(func):
    """A simple 'measure execution time decorator to be used with any
    'async' function
    """

    @wraps(func)
    async def measure_time_wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        logging.debug(
            f"Function {func.__name__}(...) took "
            f"{round((time.time() - start) * 1000)} msecs"
        )
        return result

    return measure_time_wrapper
