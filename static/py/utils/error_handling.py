
from .logging_config import logger
from rest_framework.response import Response


def throw_error(status_code, error_message, log=None, error_details=None):
    """
    Throws customized errors in a minimalistic and clean way. Used
    for sending error messages to the frontend customized for user
    experience, while minimizing exposure of backend logic. It also
    allows optional logging for debugging purposes and supports detailed
    error reporting when needed.

    Args:
        status_code (int): HTTP status code for the response.
        error_message (str): Main error message (frontend).
        log (str, optional): Log message to record. Defaults to None.
        error_details (dict or list, optional): Additional error details.
        Defaults to None.

    Returns:
        Response: DRF Response object with error data.
    """
    if log:
        logger.error(log)

    error_response = {"error_message": error_message}
    if error_details:
        error_response["error_details"] = error_details

    return Response(error_response, status=status_code)
