import inspect
from functools import wraps

from logger.log_config import BOT_LOG


class LogAdvanced:
    """Debug info logger class for tracing wrapped function calls."""

    def __init__(self, raiseable=False):
        """Set a flag in case wrapped function can potentially raise an exception."""

        self.raiseable = raiseable

    def __call__(self, func):
        """Generate debugging information to store."""

        @wraps(func)
        def wrapped(*args, **kwargs):
            full_name, function_name = self._inspect_caller()
            logger = BOT_LOG
            logger.debug(
                f'function "{func.__name__}" called from "{function_name}",'
                f" params = {args}, {kwargs}"
            )
            if not self.raiseable:
                res = func(*args, **kwargs)
                logger.debug(f'function "{func.__name__} returned: {res}')
            else:
                try:
                    res = func(*args, **kwargs)
                    logger.debug(f'function "{func.__name__} returned: {res}')
                except Exception as e:
                    logger.error(
                        f'function "{func.__name__}"'
                        f' raised an exception "{type(e).__name__}" {e.args}'
                    )
                    raise e
            return res

        return wrapped

    @staticmethod
    def _inspect_caller():
        """Gets caller file and called function names from frame inspecting."""

        prev_frame = inspect.currentframe().f_back.f_back
        (file_name, line_number, function_name, lines, index) = inspect.getframeinfo(
            prev_frame
        )

        return file_name, function_name
