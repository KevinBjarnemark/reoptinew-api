from django.conf import settings
from django.db import models
from cloudinary.models import CloudinaryField
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from static.py.utils.environment import is_development


# Custom user
class User(AbstractUser):
    pass


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    birth_date = models.DateTimeField(null=True, blank=True)
    if is_development():
        image = models.ImageField(
            upload_to='profile_images/', blank=True, null=True
        )
    else:
        image = CloudinaryField('image', blank=True, null=True)

    def clean(self):
        if self.birth_date and self.birth_date > timezone.now().date():
            raise ValidationError("Birth date cannot be in the future.")
