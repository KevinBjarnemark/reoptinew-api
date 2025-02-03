from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from static.utils.environment import image_url
from static.utils.validators import validate_image_extension
from .constants import VALIDATION_RULES
from .models import Profile


# Securely hash passwords before storing in database
User = get_user_model()


class ProfileImageUpdateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)

    class Meta:
        model = Profile
        fields = ["image"]

    def validate_image(self, image):
        # Validate image
        request = self.context.get("request")
        image = request.FILES.get("image", None)
        return validate_image_extension(image)

    def update(self, instance, validated_data):
        instance.image = validated_data["image"]
        instance.save()
        return instance


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source="user.username")
    user_id = serializers.ReadOnlyField(source="user.id")

    class Meta:
        model = Profile
        fields = [
            "id",
            "user_id",
            "birth_date",
            "image",
            "username",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Handle image
        representation["image"] = image_url(instance.image)
        # Remove birth_date if the user is not the owner
        request = self.context.get("request")
        if request.user != instance.user:
            representation.pop("birth_date", None)

        representation["followers"] = list(
            instance.user.followers.values_list(
                "follower__username", flat=True
            )
        )
        representation["following"] = list(
            instance.user.following.values_list(
                "following__username", flat=True
            )
        )

        return representation


class SignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, min_length=3)
    password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=VALIDATION_RULES["PASSWORD"]["MIN_LENGTH"],
        max_length=VALIDATION_RULES["PASSWORD"]["MAX_LENGTH"],
    )
    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=VALIDATION_RULES["PASSWORD"]["MIN_LENGTH"],
        max_length=VALIDATION_RULES["PASSWORD"]["MAX_LENGTH"],
    )
    birth_date = serializers.DateField(required=True)
    image = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "confirm_password",
            "birth_date",
            "image",
        ]

    # Overwrite default error messages with custom errors
    def __init__(self, *args, **kwargs):
        super(SignUpSerializer, self).__init__(*args, **kwargs)
        self.fields["username"].error_messages[
            "required"
        ] = "You must enter a username."
        self.fields["username"].error_messages[
            "blank"
        ] = "Username is missing."

    def validate(self, data):
        # Normalize username to lowercase for case-insensitive comparison
        normalized_username = data["username"].lower()

        # Username cannot only be digits check
        if str(normalized_username).isdigit():
            raise serializers.ValidationError(
                {"username": "Username cannot only be digits."}
            )
        # Check if username already exists, ignoring case
        if User.objects.filter(username__iexact=normalized_username).exists():
            raise serializers.ValidationError(
                {"username": "This username is already taken."}
            )
        # Check if passwords match
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."}
            )

        # Validate image
        request = self.context.get("request")
        image = request.FILES.get("image", None)
        data["image"] = validate_image_extension(image)

        return data

    def create(self, validated_data):
        # Pop validated_data entries
        validated_data.pop("confirm_password")
        birth_date = validated_data.pop("birth_date", None)

        # Access the image from request.FILES
        request = self.context.get("request")
        image = request.FILES.get("image", None)

        # Create the user instance
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
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
        fields = ["username", "password"]

    def validate(self, data):
        user = authenticate(
            username=data["username"], password=data["password"]
        )
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        data["user"] = user
        return data


# Pylint is ignored here since there is no purpose of saving/creating data
# in this serializer.
# pylint: disable=abstract-method
class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)

    def validate_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Incorrect password.")
        return value
