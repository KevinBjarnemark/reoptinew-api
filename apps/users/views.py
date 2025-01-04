from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Profile as ProfileModel
from .serializers import ProfileSerializer, SignUpSerializer
from static.py.utils.error_handling import throw_error
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import (
    DjangoModelPermissionsOrAnonReadOnly,
    AllowAny,
    IsAuthenticated
)
from static.py.utils.logging import log_debug
from rest_framework_simplejwt.tokens import RefreshToken


class UserProfile(APIView):
    # Only allow GET requests
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return ProfileModel.objects.all()

    def get(self, request):
        try:
            # Get the profile by primary key
            profile = ProfileModel.objects.get(user=request.user)
            # Serialize fields
            serializer = ProfileSerializer(
                profile,
                context={'request': request}
            )
            # Return the profile
            return Response(serializer.data, status=200)
        # Handle profile doens't exist
        except ProfileModel.DoesNotExist:
            return throw_error(
                404,
                "Profile not found.",
                log=f"Profile not found for user ID: {request.user}"
            )
        # Handle unexpected errors
        except Exception as e:
            return throw_error(
                500,
                "Something went wrong.",
                log=f"Unhandled exception: {str(e)}"
            )


class Profile(APIView):
    """Returns a profile based on the primary key"""
    # Only allow GET requests
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    http_method_names = ['get']
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return ProfileModel.objects.all()

    def get(self, request, pk):
        try:
            # Get the profile by primary key
            profile = ProfileModel.objects.get(pk=pk)
            # Serialize fields
            serializer = ProfileSerializer(
                profile,
                context={'request': request}
            )
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

    permission_classes = [AllowAny]
    # Only allow POST requests
    http_method_names = ['post']
    # Enable multipart form-data parsing for images
    parser_classes = [MultiPartParser]
    serializer_class = SignUpSerializer

    def post(self, request):
        showDebugging = True
        try:
            # Serialize incoming data
            serializer = SignUpSerializer(
                data=request.data,
                context={'request': request}
            )
            if not serializer.is_valid():
                return throw_error(
                    400,
                    "Validation failed.",
                    log=f"Validation errors: {serializer.errors}",
                    error_details=serializer.errors
                )
            # Save the user instance
            user = serializer.save()
            log_debug(showDebugging, "User created", user.username)

            # Generate JWT tokens
            refresh_token = RefreshToken.for_user(user)
            # Return a successful response with token
            return Response({
                "message": "Account successfully registered.",
                "refresh": str(refresh_token),
                "access": str(refresh_token.access_token)
            }, status=201)
        # Handle unexpected errors
        except Exception as e:
            return throw_error(
                500,
                "Something went wrong during account registration.",
                log=f"Unhandled exception: {str(e)}"
            )
