from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django.utils import timezone
from django.core.exceptions import ValidationError


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateTimeField(null=True, blank=True)
    if settings.DEBUG:
        image = models.ImageField(
            upload_to='profile_images/', blank=True, null=True
        )
    else:
        image = CloudinaryField('image', blank=True, null=True)

    def clean(self):
        if self.birth_date and self.birth_date > timezone.now().date():
            raise ValidationError("Birth date cannot be in the future.")
