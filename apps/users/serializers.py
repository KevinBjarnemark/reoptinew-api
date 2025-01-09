from rest_framework import serializers
from .models import Profile
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from .constants import VALIDATION_RULES

# Securely hash passwords before storing in database
User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Profile
        fields = [
            'id', 'birth_date', 'image', "username",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Remove birth_date if the user is not the owner
        request = self.context.get('request')
        if request.user != instance.user:
            representation.pop('birth_date', None)
        return representation


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
                {"password": "[CUSTOM] Passwords do not match."}
            )
        # Check minimum password length
        if len(data['password1']) < VALIDATION_RULES["PASSWORD"]["MIN_LENGTH"]:
            raise serializers.ValidationError(
                {
                    "password": (
                        "[CUSTOM] Password must be at least " +
                        f"{VALIDATION_RULES["PASSWORD"]["MIN_LENGTH"]} " +
                        "characters long."
                    )
                }
            )

        # Check if username already exists
        if User.objects.filter(username=data["username"]).exists():
            raise serializers.ValidationError(
                {
                    "username": "[CUSTOM] This username is already taken."
                }
            )

        # Access the image from request.FILES
        request = self.context.get('request')
        image = request.FILES.get('image', None)
        # Validate image file type
        if image:
            valid_extensions = VALIDATION_RULES["IMAGE"]["VALID_EXTENSIONS"]
            extension = image.name.split('.')[-1].lower()
            if extension not in valid_extensions:
                raise serializers.ValidationError(
                    {"image": "[CUSTOM] Invalid file type."}
                )

        return data

    def create(self, validated_data):
        # Remove the second password
        validated_data.pop('password2')
        birth_date = validated_data.pop('birth_date', None)

        # Access the image from request.FILES
        request = self.context.get('request')
        image = request.FILES.get('image', None)

        # Create the user instance
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password1'],
        )

        # Create profile linked to the user
        Profile.objects.create(
            user=user,
            birth_date=birth_date,
            image=image,
        )

        return user


class LogInSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']

    def validate(self, data):
        user = authenticate(
            username=data['username'], password=data['password']
        )
        if not user:
            raise serializers.ValidationError("[CUSTOM] Invalid credentials.")
        data['user'] = user
        return data
