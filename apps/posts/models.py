from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from static.utils.environment import is_development
from cloudinary.models import CloudinaryField

User = get_user_model()


class HarmfulToolCategory(models.Model):
    category = models.CharField(max_length=50, unique=True)

    # Display in admin portal
    def __str__(self):
        return str(self.category)


class HarmfulMaterialCategory(models.Model):
    category = models.CharField(max_length=50, unique=True)

    # Display in admin portal
    def __str__(self):
        return str(self.category)


class Post(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    public = models.BooleanField(default=True)
    harmful_post = models.BooleanField(default=False)
    instructions = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.CharField(max_length=255, null=True, blank=True)
    harmful_tool_categories = models.ManyToManyField(
        HarmfulToolCategory, related_name="posts"
    )
    harmful_material_categories = models.ManyToManyField(
        HarmfulMaterialCategory, related_name="posts"
    )
    # Image index for posts with no image attached
    default_image_index = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(0), MaxValueValidator(3)]
    )
    if is_development():
        image = models.ImageField(
            upload_to="profile_images/", blank=True, null=True
        )
    else:
        image = CloudinaryField("image", blank=True, null=True)


class Material(models.Model):
    """This model is related to the Post model"""

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="materials"
    )
    quantity = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)


class Tool(models.Model):
    """This model is related to the Post model"""

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="tools"
    )
    quantity = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)


class Like(models.Model):
    """This model is related to the Post model"""

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["post", "user"], name="unique_like"
            )
        ]

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="likes"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Rating(models.Model):
    """This model is related to the Post model"""

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["post", "user"], name="unique_rating"
            )
        ]

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="post_ratings"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="post_ratings"
    )
    saves_money = models.PositiveIntegerField(default=0)
    saves_time = models.PositiveIntegerField(default=0)
    is_useful = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    """This model is related to the Post model"""

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="post_comment"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="post_comment"
    )
    text = models.TextField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
