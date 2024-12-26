
import logging
from rest_framework.response import Response


# Set up logging
logger = logging.getLogger(__name__)


def throw_error(status_code, message, log=None):
    if log:
        logger.error(log)
    return Response({"error": message}, status=status_code)
