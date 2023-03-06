import structlog
import time
from functools import wraps

logger = structlog.stdlib.get_logger(__name__)


def async_measure_time(func):
    """A simple 'measure execution time decorator to be used with any
    'async' function
    """

    @wraps(func)
    async def measure_time_wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        logger.debug(
            "Duration",
            function_name=func.__name__,
            duration_ms=round((time.time() - start) * 1000),
        )
        return result

    return measure_time_wrapper
