import sys
from typing import Never

LOG_COLOUR: int = 2
INFO_COLOUR: int = 0
WARNING_COLOUR: int = 33
ERROR_COLOUR: int = 31


def log_exception(func):
    """Log exceptions to stderr instead of raising.

    Used by the `apply_()` functions so that an exception, when applying
    a theme, does not prevent the other themes from being applied.
    """

    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            error(f'exception during "{func.__name__}()": {str(e)}')

    return wrapper


def format_msg(colour: int, prefix: bool, msg: str) -> str:
    return f"\033[{colour}m{':: ' if prefix else ''}{msg}\033[0m"


def log(msg: str, prefix: bool = True) -> None:
    print(format_msg(LOG_COLOUR, prefix, msg))


def info(msg: str, prefix: bool = True) -> None:
    print(format_msg(INFO_COLOUR, prefix, msg))


def warn(msg: str, prefix: bool = True) -> None:
    print(format_msg(WARNING_COLOUR, prefix, f"Warning: {msg}"))


def error(err: str | Exception, prefix: bool = True) -> None:
    print(format_msg(ERROR_COLOUR, prefix, f"Error: {err}"), file=sys.stderr)


def fatal(err: str | Exception, prefix: bool = True) -> Never:
    print(format_msg(ERROR_COLOUR, prefix, f"Fatal: {err}"), file=sys.stderr)
    sys.exit(1)
