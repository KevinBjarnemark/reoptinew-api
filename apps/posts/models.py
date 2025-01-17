from django.db import models
from django.contrib.auth import get_user_model
from static.py.utils.environment import is_development
from cloudinary.models import CloudinaryField

User = get_user_model()


class HarmfulTool(models.Model):
    name = models.CharField(max_length=50, unique=True)

    # Display in admin portal
    def __str__(self):
        return str(self.name)


class HarmfulMaterial(models.Model):
    name = models.CharField(max_length=50, unique=True)

    # Display in admin portal
    def __str__(self):
        return str(self.name)


class Post(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    public = models.BooleanField(default=True)
    instructions = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.CharField(max_length=255, null=True, blank=True)
    harmful_tools = models.ManyToManyField(
        HarmfulTool, blank=True, related_name='posts'
    )
    harmful_materials = models.ManyToManyField(
        HarmfulMaterial, blank=True, related_name='posts'
    )
    if is_development():
        image = models.ImageField(
            upload_to='profile_images/', blank=True, null=True
        )
    else:
        image = CloudinaryField('image', blank=True, null=True)
