from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Profile as ProfileModel
from .serializers import ProfileSerializer, SignUpSerializer
from static.py.utils.error_handling import throw_error
from django.contrib.auth import login, authenticate
from static.py.utils.logging_config import logger
from rest_framework.parsers import MultiPartParser


class Profile(APIView):
    """Returns a profile based on the primary key"""
    # Only allow GET requests
    http_method_names = ['get']

    def get(self, request, pk):
        try:
            # Get the profile by primary key
            profile = ProfileModel.objects.get(pk=pk)
            # Serialize fields
            serializer = ProfileSerializer(profile)
            # Return the profile
            return Response(serializer.data, status=200)
        # Handle profile doens't exist
        except ProfileModel.DoesNotExist:
            return throw_error(
                404,
                "Profile not found.",
                log=f"Profile not found for user ID: {pk}"
            )
        # Handle unexpected errors
        except Exception as e:
            return throw_error(
                500,
                "Something went wrong.",
                log=f"Unhandled exception: {str(e)}"
            )


class SignUp(APIView):
    """
    Registers a user account with username and password.
    """
    # Only allow POST requests
    http_method_names = ['post']
    # Enable multipart form-data parsing for images
    parser_classes = [MultiPartParser]

    def post(self, request):
        try:
            # Serialize incoming data
            serializer = SignUpSerializer(data=request.data)
            if not serializer.is_valid():
                return throw_error(
                    400,
                    "Validation failed.",
                    log=f"Validation errors: {serializer.errors}",
                    error_details=serializer.errors
                )
            # Save the user instance
            user = serializer.save()
            logger.debug(f"User created: {user.username}")
            # Authenticate and log in the user
            username = user.username
            password = request.data['password1']
            logger.debug(f"Authenticating user: {username}")
            user = authenticate(username=username, password=password)
            # Handle failed authentication
            if user is None:
                logger.debug("Authentication failed.")
                return throw_error(
                    401,
                    "Authentication failed.",
                    log="User could not be authenticated after registration."
                )
            logger.debug(f"Logging in user: {username}")
            login(request, user)

            # Return a successful response
            return Response(
                {"message": "Account successfully registered."}, status=201
            )
        # Handle unexpected errors
        except Exception as e:
            return throw_error(
                500,
                "Something went wrong during account registration.",
                log=f"Unhandled exception: {str(e)}"
            )
