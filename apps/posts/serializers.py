from rest_framework import serializers
from django.contrib.auth import get_user_model
from static.py.utils.environment import image_url
from static.py.utils.logging import log_debug
from static.py.utils.convert import parse_stringified_object
from .models import (
    Post,
    HarmfulMaterialCategory,
    HarmfulToolCategory,
    Tool,
    Material,
)
from .fields.list_of_primitive_dict_field import ListOfPrimitiveDictField

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

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'description',
            'instructions',
            'harmful_material_categories',
            'harmful_tool_categories',
            'created_at',
            'author',
            'tools',
            'materials',
            'default_image_index',
            'harmful_post',
        ]
        read_only_fields = ['id', 'created_at', 'author']

    def get_author(self, obj):
        """
        Returns a dictionary with author's details: id, username, and image.
        """
        user = obj.user
        profile = user.profile

        return {
            'id': user.id,
            'username': user.username,
            'image': image_url(profile.image),
        }

    def to_representation(self, instance):
        """
        Custom representation for ManyToMany fields.

        This method ensures scalability by connecting ManyToMany fields
        into the post, instead of writing duplicate data.
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

        # Include related tools and materials
        representation["tools"] = [
            {
                "quantity": tool.quantity,
                "name": tool.name,
                "description": tool.description,
            }
            for tool in instance.tools.all()
        ]

        representation["materials"] = [
            {
                "quantity": material.quantity,
                "name": material.name,
                "description": material.description,
            }
            for material in instance.materials.all()
        ]

        request = self.context.get('request', None)
        # Include likes object
        representation["likes"] = {
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

    def validate_harmful_tool_categories(self, value):
        """
        Validates harmful tool_categories, ensuring all names exist in
        the database.
        """
        # Since this is multipart/formdata, parse the stringified object
        parsed_value = parse_stringified_object(value)

        # Fetch all valid names from the database
        valid_tools = set(
            HarmfulToolCategory.objects.filter(
                category__in=parsed_value
            ).values_list("category", flat=True)
        )
        if isinstance(parsed_value, list) and parsed_value:
            for tool in parsed_value:
                if tool not in valid_tools:
                    raise serializers.ValidationError(
                        {
                            "harmful_tool_category": "You entered a "
                            + f"tool category that is not allowed ({tool})."
                        }
                    )

        return parsed_value

    def validate_harmful_material_categories(self, value):
        """
        Validates harmful material_categories, ensuring all names exist
        in the database.
        """

        # Since this is multipart/formdata, parse the stringified object
        parsed_value = parse_stringified_object(value)

        # Fetch all valid names from the database
        valid_materials = set(
            HarmfulMaterialCategory.objects.filter(
                category__in=parsed_value
            ).values_list("category", flat=True)
        )
        if isinstance(parsed_value, list) and parsed_value:
            for material in parsed_value:
                if material not in valid_materials:
                    raise serializers.ValidationError(
                        {
                            "harmful_material_category": "You entered "
                            + "a material category that is not allowed "
                            + f'({material}).'
                        }
                    )

        return parsed_value

    def create(self, validated_data):
        show_debugging = True
        log_debug(show_debugging, "Creating a post", validated_data)
        # Pop harmful_tool_categories and harmful_material_categories from
        # validated data
        harmful_tool_categories_data = validated_data.pop(
            'harmful_tool_categories', []
        )
        harmful_material_categories_data = validated_data.pop(
            'harmful_material_categories', []
        )
        tools_data = validated_data.pop('tools', [])
        materials_data = validated_data.pop('materials', [])

        # Create the post
        post = Post.objects.create(
            # Associate the authenticated user
            user=self.context['request'].user,
            **validated_data,
        )

        # Add related tools
        for tool in tools_data:
            Tool.objects.create(post=post, **tool)

        # Add related materials
        for material in materials_data:
            Material.objects.create(post=post, **material)

        # Add ManyToMany relationships
        for tool_category in harmful_tool_categories_data:
            tool, _ = HarmfulToolCategory.objects.get_or_create(
                category=tool_category
            )
            post.harmful_tool_categories.add(tool)

        for material_category in harmful_material_categories_data:
            material, _ = HarmfulMaterialCategory.objects.get_or_create(
                category=material_category
            )
            post.harmful_material_categories.add(material)

        return post
