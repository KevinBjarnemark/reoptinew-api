
import logging
from static.py.utils.environment import is_development
from static.py.utils.inspect_stack import get_file_name_of_caller
from django.conf import settings

logger = logging.getLogger("app")


def log_debug(log, name, *args):
    """
    Logs debugging messages to the console in development.

    Args:
        log (bool): Extra conditional for toggling debugging.
        name (str): Name/identifier of the log.
        *args: Any number of additional arguments to log.
    """
    if (log or settings.SHOW_ALL_LOGS) and is_development():
        # Get the file name of the caller
        caller_file = get_file_name_of_caller(2)
        message = (
            f"(Occurred in {caller_file}) {name}: " +
            " ".join(map(str, args))
        )
        logger.debug(message)


def log_message(log, name, *args):
    """
    Logs general messages to the console in development.

    Args:
        log (bool): Extra conditional for toggling logging.
        name (str): Name/identifier of the log.
        *args: Any number of additional arguments to log.
    """
    if (log or settings.SHOW_ALL_LOGS) and is_development():
        # Get the file name of the caller
        caller_file = get_file_name_of_caller(2)
        message = (
            f"(Occurred in {caller_file}) {name}: " +
            " ".join(map(str, args))
        )
        logger.info(message)


def log_error(log, name, *args):
    """
    Logs errors to the console in development.

    Args:
        log (bool): Extra conditional for toggling logging.
        name (str): Name/identifier of the log.
        *args: Any number of additional arguments to log.
    """
    if (log or settings.SHOW_ALL_LOGS) and is_development():
        # Get the file name of the caller
        caller_file = get_file_name_of_caller(2)
        message = (
            f"(Occurred in {caller_file}) {name}: " +
            " ".join(map(str, args))
        )
        logger.error(message)
