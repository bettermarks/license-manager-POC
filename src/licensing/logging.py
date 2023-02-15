import logging

"""
Thanks to https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
"""

class Loglevel:
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL= "critical"


class ColorFormatter(logging.Formatter):

    blue = "\x1b[36;20m"
    grey = "\x1b[38;20m"
    green = "\x1b[32;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: blue + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_loglevel(loglevel: str) -> int:
    """my configurable 'string' loglevel to internal int loglevel"""
    match loglevel:
        case Loglevel.DEBUG:
            return logging.DEBUG
        case Loglevel.INFO:
            return logging.INFO
        case Loglevel.WARNING:
            return logging.WARNING
        case Loglevel.ERROR:
            return logging.ERROR
        case _:
            return logging.CRITICAL