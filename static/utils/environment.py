from django.conf import settings
from decouple import config


def is_development():
    """
    Check if the application is running in development mode.
    Returns:
        bool: True if in development mode, otherwise False.
    """
    return settings.DEBUG


def image_url(image_field):
    """
    Dynamically returns the full image URL based on development
    and production environments.

    Args:
        image_field: The image field (e.g., instance.image) to generate the
        full URL for.

    Returns:
        str: The full URL for the image, or None if the image field is empty.
    """
    if not image_field:
        return None

    # Get the development server URL from environment variables
    dev_server_host = config('DEV_SERVER_HOST')
    dev_server_port = config('DEV_SERVER_PORT')

    # Return the URL with or without the development server prefix
    if is_development():  # Development environment
        # Build the image url from environment variables
        return (
            f"http://{dev_server_host}:{int(dev_server_port)}{image_field.url}"
        )
    return image_field.url  # Production environment
