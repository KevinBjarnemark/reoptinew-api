
from .logging import logger
from rest_framework.response import Response
from static.py.utils.inspect_stack import get_file_name_of_caller


def throw_error(status_code, error_message, log=None, error_details=None):
    """
    Builds a dictionary designed to provide a seamless experience when
    sent to the frontend. It also allows optional logging for debugging
    purposes and supports detailed error reporting when needed.

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
        # Get the file name of the caller
        caller_file = get_file_name_of_caller(2)
        occurred_in = f"(Occurred in {caller_file} by throw_error()) "
        logger.error(
            f"{occurred_in} {{"
            f"  'status_code': {status_code},"
            f"  'error_message': '{error_message}',"
            f"  'log': '{log}',"
            f"  'error_details': {error_details},"
            f"}}"
        )

    def process_errors(errors):
        sanitized_errors = {}
        for field, messages in errors.items():
            sanitized_messages = []
            for msg in messages:
                logger.debug(
                    f"\nField: {field}\nmsg: {msg}\ncode: {msg.code}\n"
                )
                sanitized_messages.append(msg)
                if log:
                    logger.debug(
                        "Appending custom error --> " +
                        f"{field}: '{msg}'"
                    )
                sanitized_errors[field] = sanitized_messages
        return sanitized_errors

    error_response = {"error_message": error_message}
    if error_details:
        sanitized_details = process_errors(error_details)
        error_response["error_details"] = sanitized_details

    return Response(error_response, status=status_code)
