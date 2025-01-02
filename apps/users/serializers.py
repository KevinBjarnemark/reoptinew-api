from rest_framework import serializers
from .models import Profile
from django.contrib.auth import get_user_model

# Securely hash passwords before storing in database
User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Profile
        fields = [
            'id', 'birth_date', 'image', "username",
        ]


class SignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password1 = serializers.CharField(required=True, write_only=True)
    password2 = serializers.CharField(required=True, write_only=True)
    birth_date = serializers.DateField(required=True)
    image = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'birth_date', 'image']

    def validate(self, data):
        # Check if passwords match
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."}
            )
        return data

    def create(self, validated_data):
        # Remove the second password
        validated_data.pop('password2')
        birth_date = validated_data.pop('birth_date', None)
        image = validated_data.pop('image', None)

        # Create the user instance
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password1'],
        )

        # Create profile linked to the user
        Profile.objects.create(user=user, birth_date=birth_date, image=image)

        return user
