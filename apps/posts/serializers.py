from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post


# Securely hash passwords before storing in database
User = get_user_model()


class PostSerializer(serializers.ModelSerializer):
    # Custom field for embedding author details
    author = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'description',
            'instructions',
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
            # Return image URL or None
            'image': profile.image.url if profile.image else None,
        }

    def create(self, validated_data):
        # Associate the authenticated user with the post
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
