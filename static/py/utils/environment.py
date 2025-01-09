from django.conf import settings


def is_development():
    """
    Check if the application is running in development mode.
    Returns:
        bool: True if in development mode, otherwise False.
    """
    return settings.DEBUG
