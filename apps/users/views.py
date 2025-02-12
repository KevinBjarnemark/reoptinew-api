from static.utils.error_handling import throw_error
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from static.utils.logging import log_debug
from .models import Profile as ProfileModel, Follow
from .serializers import (
    ProfileSerializer,
    SignUpSerializer,
    LogInSerializer,
    DeleteAccountSerializer,
    ProfileImageUpdateSerializer,
)

User = get_user_model()


class Profile(APIView):
    """Returns a profile based on either the userid or
    the username"""

    # Only allow GET requests
    permission_classes = [AllowAny]
    http_method_names = ["get"]
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return ProfileModel.objects.all()

    def get(self, request, identifier=None):
        show_debugging = True
        try:
            log_debug(
                show_debugging,
                "Loading a user's profile, received identifier:",
                identifier,
            )
            # Get the user's profile if there's no identifier in the
            # request.
            if not identifier and request.user:
                profile = ProfileModel.objects.get(user=request.user)
            else:
                # Get a specific user's profile when there's an identifier
                # in the request.
                if str(identifier).isdigit():
                    # Lookup profile by user ID
                    profile = get_object_or_404(
                        ProfileModel, user__id=identifier
                    )
                else:
                    # Lookup profile by username
                    profile = get_object_or_404(
                        ProfileModel, user__username__iexact=identifier
                    )

            # Serialize fields
            serializer = ProfileSerializer(
                profile, context={"request": request}
            )
            # Return the profile
            return Response(serializer.data, status=200)
        # Handle profile doens't exist
        except ProfileModel.DoesNotExist:
            return throw_error(
                404,
                "Profile not found.",
                log=f"Profile not found for user ID: {identifier}",
            )
        # Handle unexpected errors
        except Exception as e:
            return throw_error(
                500,
                "Something went wrong.",
                log=f"Unhandled exception: {str(e)}",
            )


class SignUp(APIView):
    """
    Registers a user account with username and password.
    """

    permission_classes = [AllowAny]
    # Only allow POST requests
    http_method_names = ["post"]
    # Enable multipart form-data parsing for images
    parser_classes = [MultiPartParser]
    serializer_class = SignUpSerializer

    def post(self, request):
        show_debugging = True
        try:
            # Serialize incoming data
            serializer = SignUpSerializer(
                data=request.data, context={"request": request}
            )
            if not serializer.is_valid():
                return throw_error(
                    400,
                    "Validation failed.",
                    log=f"Validation errors: {serializer.errors}",
                    error_details=serializer.errors,
                )
            # Save the user instance
            user = serializer.save()
            log_debug(show_debugging, "User created", user.username)

            # Generate JWT tokens
            refresh_token = RefreshToken.for_user(user)
            # Return a successful response with token
            return Response(
                {
                    "message": "Account successfully registered.",
                    "refresh": str(refresh_token),
                    "access": str(refresh_token.access_token),
                },
                status=201,
            )
        # Handle unexpected errors
        except Exception as e:
            return throw_error(
                500,
                "Something went wrong during account registration.",
                log=f"Unhandled exception: {str(e)}",
            )


class LogIn(APIView):
    """
    Registers a user account with username and password.
    """

    permission_classes = [AllowAny]
    # Only allow POST requests
    http_method_names = ["post"]
    # Enable multipart form-data parsing for images
    parser_classes = [MultiPartParser]
    serializer_class = LogInSerializer

    def post(self, request):
        show_debugging = True
        try:
            # Serialize incoming data
            serializer = LogInSerializer(data=request.data)
            if not serializer.is_valid():
                return throw_error(
                    400,
                    "Validation failed.",
                    log=f"Validation errors: {serializer.errors}",
                    error_details=serializer.errors,
                )
            user = serializer.validated_data["user"]
            log_debug(show_debugging, "User authenticated", user.username)

            # Generate JWT tokens
            refresh_token = RefreshToken.for_user(user)
            # Return a successful response with token
            return Response(
                {
                    "message": "Login successful.",
                    "refresh": str(refresh_token),
                    "access": str(refresh_token.access_token),
                },
                status=201,
            )
        # Handle unexpected errors
        except Exception as e:
            return throw_error(
                500,
                "Something went wrong during login.",
                log=f"Unhandled exception: {str(e)}",
            )


class LogOut(APIView):
    """
    Logs out the user by blacklisting their refresh token.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        show_debugging = True
        try:
            log_debug(show_debugging, "Logging out user", "")
            # Extract the refresh token from the request
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return throw_error(
                    400,
                    "Invalid token",
                    log=f"Invalid token: {str(refresh_token)}",
                )
            log_debug(show_debugging, "Received refresh token ", refresh_token)

            # Blacklist the refresh token
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                return throw_error(
                    400,
                    "Log out failed",
                    log=f"Token blacklisting failed: {str(e)}",
                )

            return Response(
                {"message": "Successfully logged out."}, status=200
            )
        except Exception as e:
            return throw_error(
                500,
                "Something went wrong during logout.",
                log=f"Unhandled exception: {str(e)}",
            )


class DeleteAccount(APIView):
    """
    Deletes a user's account.
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request):
        show_debugging = True
        try:
            # Serialize incoming data
            serializer = DeleteAccountSerializer(
                data=request.data, context={"request": request}
            )
            if not serializer.is_valid():
                return throw_error(
                    400,
                    "Validation failed.",
                    log=f"Validation errors: {serializer.errors}",
                    error_details=serializer.errors,
                )
            log_debug(
                show_debugging,
                "User is valid, proceeding with account deletion.",
                "",
            )
            # Delete the user's account
            user = request.user
            user.delete()

            # Return a successful response
            return Response(
                {
                    "message": "Deleted account successfully.",
                },
                status=200,
            )
        # Handle unexpected errors
        except Exception as e:
            return throw_error(
                500,
                "Something went wrong during account deletion.",
                log=f"Unhandled exception: {str(e)}",
            )


class UpdateProfileImage(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    http_method_names = ["get", "post", "patch"]

    def patch(self, request):
        try:
            profile = ProfileModel.objects.get(user=request.user)
            serializer = ProfileImageUpdateSerializer(
                profile,
                data=request.data,
                context={"request": request},
                partial=True,
            )

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "Profile image updated successfully."},
                    status=200,
                )
            return throw_error(
                400,
                "Validation failed.",
                log="Rejected update post request (serializer).",
                error_details=serializer.errors,
            )

        except ProfileModel.DoesNotExist:
            return throw_error(
                404,
                "Profile not found.",
                log="User tried to update a post but "
                + "the profile model doens't exist.",
            )
        except Exception as e:
            return throw_error(500, "Something went wrong.", log=str(e))


class FollowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        try:
            if not pk:
                return throw_error(400, "User ID is required.")

            if request.user.id == int(pk):
                return throw_error(400, "You cannot follow yourself.")

            user_to_follow = User.objects.get(id=pk)

            follow, created = Follow.objects.get_or_create(
                follower=request.user, following=user_to_follow
            )
            if created:
                return Response(
                    {"message": "Followed successfully!", "id": follow.id},
                    status=201,
                )
            return throw_error(400, "You are already following this user.")
        except User.DoesNotExist:
            return throw_error(404, "User not found.")
        except Exception as e:
            return throw_error(500, "Unable to follow user.", log=str(e))

    def delete(self, request, pk=None):
        try:
            if not pk:
                return throw_error(400, "User ID is required.")

            follow = Follow.objects.filter(
                follower=request.user, following_id=pk
            ).first()
            if follow:
                follow.delete()
                return Response(
                    {"message": "Unfollowed successfully!"}, status=200
                )
            return throw_error(400, "You are not following this user.")
        except Exception as e:
            return throw_error(500, "Unable to unfollow user.", log=str(e))
