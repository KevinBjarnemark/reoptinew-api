from rest_framework import serializers
from django.contrib.auth import get_user_model
from static.py.utils.environment import image_url
from static.py.utils.logging import log_debug
from static.py.utils.convert import parse_stringified_object
from .models import Post, HarmfulMaterial, HarmfulTool


# Securely hash passwords before storing in database
User = get_user_model()


class PostSerializer(serializers.ModelSerializer):
    # Custom field for embedding author details
    author = serializers.SerializerMethodField()
    # Writable fields for ManyToMany input
    harmful_tools = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        default=list,
    )
    harmful_materials = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        default=list,
    )

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'description',
            'instructions',
            'harmful_materials',
            'harmful_tools',
            'created_at',
            'author',
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
        representation["harmful_tools"] = [
            {"id": tool.id, "name": tool.name}
            for tool in instance.harmful_tools.all()
        ]
        representation["harmful_materials"] = [
            {"id": material.id, "name": material.name}
            for material in instance.harmful_materials.all()
        ]
        return representation

    def validate_harmful_tools(self, value):
        """
        Validates harmful tools, ensuring all names exist in the database.
        """
        # Since this is multipart/formdata, parse the stringified object
        parsed_value = parse_stringified_object(value)

        # Fetch all valid names from the database
        valid_tools = set(
            HarmfulTool.objects.filter(name__in=parsed_value).values_list(
                "name", flat=True
            )
        )
        if isinstance(parsed_value, list) and parsed_value:
            for material in parsed_value:
                if material not in valid_tools:
                    raise serializers.ValidationError(
                        {
                            "harmful_material": "You entered a material that "
                            + f"is not allowed ({material})."
                        }
                    )

        return parsed_value

    def validate_harmful_materials(self, value):
        """
        Validates harmful materials, ensuring all names exist in the database.
        """

        # Since this is multipart/formdata, parse the stringified object
        parsed_value = parse_stringified_object(value)

        # Fetch all valid names from the database
        valid_materials = set(
            HarmfulMaterial.objects.filter(name__in=parsed_value).values_list(
                "name", flat=True
            )
        )
        if isinstance(parsed_value, list) and parsed_value:
            for material in parsed_value:
                if material not in valid_materials:
                    raise serializers.ValidationError(
                        {
                            "harmful_material": "You entered a material that "
                            + f"is not allowed ({material})."
                        }
                    )

        return parsed_value

    def create(self, validated_data):
        show_debugging = True
        log_debug(show_debugging, "Creating a post", validated_data)
        # Pop harmful_tools and harmful_materials from validated data
        harmful_tools_data = validated_data.pop('harmful_tools', [])
        harmful_materials_data = validated_data.pop('harmful_materials', [])

        # Create the post
        post = Post.objects.create(
            # Associate the authenticated user
            user=self.context['request'].user,
            **validated_data,
        )
        # Add ManyToMany relationships
        for tool_name in harmful_tools_data:
            tool, _ = HarmfulTool.objects.get_or_create(name=tool_name)
            post.harmful_tools.add(tool)

        for material_name in harmful_materials_data:
            material, _ = HarmfulMaterial.objects.get_or_create(
                name=material_name
            )
            post.harmful_materials.add(material)

        return post
