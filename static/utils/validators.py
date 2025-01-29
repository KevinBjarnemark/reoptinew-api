from rest_framework import serializers
from static.utils.constants import GLOBAL_VALIDATION_RULES


def validate_image_extension(image):
    """
    Validates the file extension of an uploaded image.
    """
    if not image:
        return None  # No image provided, return None

    valid_extensions = GLOBAL_VALIDATION_RULES["IMAGE"]["VALID_EXTENSIONS"]
    extension = image.name.split(".")[-1].lower()

    if extension not in valid_extensions:
        raise serializers.ValidationError({"image": "Invalid file type."})

    # Return the image if valid
    return image
