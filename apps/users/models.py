from django.conf import settings
from django.db import models
from cloudinary.models import CloudinaryField
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from static.py.utils.environment import is_development


# Custom user
class User(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser.

    This class serves as a base for customization of the default user model.
    Currently, no additional fields or methods are defined, but this model
    allows for future extensions.

    Inherits:
        AbstractUser: Provides default fields like username,
        email, and password.
    """


class Profile(models.Model):
    """
    The user profile model.

    Represents the user profile model.

    This model extends the default user model with additional fields such as
    birth date and an optional profile image.

    Attributes:
        user (OneToOneField): A one-to-one relationship with the user model.
        birth_date (DateTimeField): The user's birth date, this field
            is mandatory.
        image (ImageField or CloudinaryField): An optional profile image field.

    Methods:
        clean():
            Validates that the birth date is not in the future.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    birth_date = models.DateField()  # Required
    if is_development():
        image = models.ImageField(
            upload_to='profile_images/', blank=True, null=True
        )
    else:
        image = CloudinaryField('image', blank=True, null=True)

    def clean(self):
        if self.birth_date and self.birth_date > timezone.now().date():
            raise ValidationError("Birth date cannot be in the future.")
