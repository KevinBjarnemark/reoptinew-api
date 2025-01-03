
import inspect
import os


def get_file_name_of_caller(level):
    """
    Returns the file name of the caller.

    Args:
        level (int): Index depth
    Returns:
        str: The file name of the calling function/module.
    """
    try:
        caller_frame = inspect.stack()[level]
        caller_file = os.path.basename(caller_frame.filename)
        return caller_file
    except IndexError:
        return None
