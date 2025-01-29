from rest_framework import serializers
from django.contrib.auth import get_user_model
from static.utils.environment import image_url
from static.utils.logging import log_debug
from static.utils.validators import validate_image_extension
from .models import (
    Post,
    HarmfulMaterialCategory,
    HarmfulToolCategory,
)
from .fields.list_of_primitive_dict_field import ListOfPrimitiveDictField
from .utils import handle_post_submission, validate_harmful_category


# Securely hash passwords before storing in database
User = get_user_model()


class PostSerializer(serializers.ModelSerializer):
    # Custom field for embedding author details
    author = serializers.SerializerMethodField()
    # Writable fields for ManyToMany input
    harmful_tool_categories = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        default=list,
    )
    harmful_material_categories = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        default=list,
    )
    materials = ListOfPrimitiveDictField(
        write_only=True, required=False, default=list
    )
    tools = ListOfPrimitiveDictField(
        write_only=True, required=False, default=list
    )
    image = serializers.ImageField(required=False)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "description",
            "instructions",
            "harmful_material_categories",
            "harmful_tool_categories",
            "created_at",
            "author",
            "tools",
            "materials",
            "default_image_index",
            "harmful_post",
            "tags",
            "image",
        ]
        read_only_fields = ["id", "created_at", "author"]

    def get_author(self, obj):
        """
        Returns a dictionary with author's details: id, username, and image.
        """
        user = obj.user
        profile = user.profile

        return {
            "id": user.id,
            "username": user.username,
            "image": image_url(profile.image),
        }

    def to_representation(self, instance):
        """
        Custom representation
        """
        representation = super().to_representation(instance)

        # Include full object details for ManyToMany relationships
        representation["harmful_tool_categories"] = [
            tool.category for tool in instance.harmful_tool_categories.all()
        ]
        representation["harmful_material_categories"] = [
            material.category
            for material in instance.harmful_material_categories.all()
        ]

        # Helper function for handling harmful content
        def serialize_related_objects(queryset):
            return [
                {
                    field: getattr(obj, field)
                    for field in ["quantity", "name", "description"]
                }
                for obj in queryset
            ]

        # Include tools
        representation["tools"] = serialize_related_objects(
            instance.tools.all()
        )
        # Include materials
        representation["materials"] = serialize_related_objects(
            instance.materials.all()
        )

        # Include likes
        request = self.context.get("request", None)
        # Include likes object
        representation["likes"] = {
            # Determine if the user has liked this post
            "user_has_liked": (
                instance.likes.filter(user=request.user).exists()
                if request
                and hasattr(request, "user")
                and request.user.is_authenticated
                else False
            ),
            "count": instance.likes.count(),
        }

        return representation

    # Pylint disabled because DRF incorrectly assumes this parameter is
    # always needed.
    # pylint: disable=unused-argument
    def validate_image(self, data):
        # Validate image
        request = self.context.get("request")
        image = request.FILES.get("image", None)
        return validate_image_extension(image)

    def validate_harmful_tool_categories(self, value):
        return validate_harmful_category(
            value, HarmfulToolCategory, "tool category"
        )

    def validate_harmful_material_categories(self, value):
        return validate_harmful_category(
            value, HarmfulMaterialCategory, "material category"
        )

    def create(self, validated_data):
        show_debugging = True
        log_debug(show_debugging, "Creating a post", validated_data)

        # Pop validated_data entries
        harmful_tool_categories_data = validated_data.pop(
            "harmful_tool_categories", []
        )
        harmful_material_categories_data = validated_data.pop(
            "harmful_material_categories", []
        )
        tools_data = validated_data.pop("tools", [])
        materials_data = validated_data.pop("materials", [])

        # Create the post
        post = Post.objects.create(
            # Associate the authenticated user
            user=self.context["request"].user,
            **validated_data,
        )
        # Handle related objects
        handle_post_submission(
            post,
            tools_data,
            materials_data,
            harmful_tool_categories_data,
            harmful_material_categories_data,
        )

        return post

    def update(self, instance, validated_data):
        show_debugging = True
        log_debug(show_debugging, "Updating a post", validated_data)

        # Pop validated_data entries
        harmful_tool_categories_data = validated_data.pop(
            "harmful_tool_categories", []
        )
        harmful_material_categories_data = validated_data.pop(
            "harmful_material_categories", []
        )
        tools_data = validated_data.pop("tools", [])
        materials_data = validated_data.pop("materials", [])

        # Delete the image if it's missing in the request
        if "image" not in validated_data:
            if instance.image:
                # Delete image
                instance.image.delete(save=False)
                # Set the field to None
                instance.image = None

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle related objects
        handle_post_submission(
            instance,
            tools_data,
            materials_data,
            harmful_tool_categories_data,
            harmful_material_categories_data,
            clear_existing=True,
        )

        return instance
