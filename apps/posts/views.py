from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    AllowAny,
    IsAuthenticated,
)
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from static.utils.error_handling import throw_error
from static.utils.logging import log_debug
from static.utils.helpers import user_is_mature
from static.utils.convert import convert_str_to_complex_obj
from static.utils.constants import GLOBAL_VALIDATION_RULES
from .serializers import PostSerializer
from .models import Post, Like


def age_restricted_error():
    return throw_error(
        400,
        "You must be at least "
        + str(GLOBAL_VALIDATION_RULES["AGE_RESTRICTED_CONTENT_AGE"])
        + " years old to create, edit, and view a post that is  "
        + "considered to be inappropriate for children.",
        log="Blocked a user from viewing, updating, or creating a post, "
        + "the user is not old enough.",
    )


class PostAPIView(APIView):
    # Override permissions for specific actions
    def get_permissions(self):
        if self.request.method == "POST":
            action = self.request.data.get("action", "create")
            if action == "filter":
                return [
                    # Allow unauthenticated users to filter posts
                    AllowAny()
                ]
        return [
            # Authenticated for all other actions
            IsAuthenticatedOrReadOnly()
        ]

    def get(self, request, pk=None):
        show_debugging = True
        show_post_data_debugging = False
        try:
            if pk:
                # Single post request
                single_post = self.filter_age_restricted_content(
                    Post.objects.get(pk=pk)
                )

                serializer = PostSerializer(
                    single_post, context={"request": request}
                )
                log_debug(
                    show_post_data_debugging,
                    "Returning single post to the client.",
                    serializer.data,
                )
                return Response(serializer.data, status=200)

            # List all posts
            posts = self.filter_age_restricted_content(Post.objects.all())
            serializer = PostSerializer(
                posts, many=True, context={"request": request}
            )

            log_debug(
                show_post_data_debugging,
                "Returning post(s) to the client.",
                serializer.data,
            )
            return Response(serializer.data, status=200)

        except PermissionDenied as e:
            # Specifically handle PermissionDenied errors
            log_debug(
                show_debugging,
                "Access forbidden for the requested post or posts.",
                str(e),
            )
            return Response(
                {
                    "message": "You must be authenticated and at least "
                    + str(
                        GLOBAL_VALIDATION_RULES["AGE_RESTRICTED_CONTENT_AGE"]
                    )
                    + " years old to view this post."
                },
                status=403,
            )

    def post(self, request):
        show_debugging = True
        try:
            log_debug(
                show_debugging,
                "POST request! (posts)",
                request.data,
            )
            # Request type
            action = request.data.get("action", "create")

            # Handle search/filter action
            if action == "filter":
                try:
                    log_debug(
                        show_debugging,
                        "This is a filter request, not a post "
                        + "creation request",
                        "",
                    )
                    filters = request.data.get("filters", {})
                    posts = self.filter_posts(filters)
                    serializer = PostSerializer(
                        posts,
                        many=True,
                        context={"request": request},
                    )
                    return Response(serializer.data, status=200)
                except Exception as e:
                    return throw_error(
                        500, "Unable to filter posts.", log=str(e)
                    )

            # Handle post creation (default)

            # Request body (mutable copy)
            data = request.data.copy()
            # Convert stringified FormData (js)
            convert_str_to_complex_obj(
                show_debugging, data, ["tools", "materials"]
            )

            # Return an error if the user is not mature enough to create post
            if not self.check_maturity():
                log_debug(
                    show_debugging,
                    "User is not old enough to create post.",
                    "",
                )
                return age_restricted_error()

            serializer = PostSerializer(
                data=data, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()  # Create post
                return Response(serializer.data, status=201)
            return throw_error(
                400,
                "Validation failed.",
                log=serializer.errors,
                error_details=serializer.errors,
            )
        except Exception as e:
            return throw_error(500, "Unable to create post.", log=str(e))

    def put(self, request, pk=None):
        show_debugging = True
        try:
            log_debug(
                show_debugging,
                f"PUT request! (posts) post id: {pk}",
                request.data,
            )
            if not pk:
                return throw_error(400, "Post ID is required for updates.")

            # Fetch the post
            try:
                post = Post.objects.get(pk=pk)
            except Post.DoesNotExist:
                return throw_error(404, "Post not found.")

            # User must be the owner of the post
            if post.user != request.user:
                return throw_error(
                    403, "You are not allowed to edit this post."
                )

            # Request body (mutable copy)
            data = request.data.copy()
            # Convert stringified FormData (js)
            convert_str_to_complex_obj(
                show_debugging, data, ["tools", "materials"]
            )

            # Return an error if the user is not mature enough to create post
            if not self.check_maturity():
                log_debug(
                    show_debugging,
                    "User is not old enough to update this post with "
                    + "the current content.",
                    "",
                )
                return age_restricted_error()

            # Validate and update the post
            serializer = PostSerializer(
                post, data=data, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()  # Update the post
                return Response(serializer.data, status=200)

            return throw_error(
                400,
                "Validation failed.",
                log=serializer.errors,
                error_details=serializer.errors,
            )
        except Exception as e:
            return throw_error(500, "Unable to update post.", log=str(e))

    def check_maturity(self):
        """
        Returns True if the user is older than the
        AGE_RESTRICTED_CONTENT_AGE constant variable, False otherwise.
        """
        profile = getattr(self.request.user, "profile", None)
        if not user_is_mature(
            profile.birth_date,
            GLOBAL_VALIDATION_RULES["AGE_RESTRICTED_CONTENT_AGE"],
        ):
            return False
        return True

    def filter_age_restricted_content(self, posts):
        """
        Filters posts based on the user's authentication and maturity.
        Guests and users under 16 can only see safe posts.
        """
        # Handle single instance (not a queryset)
        if isinstance(posts, Post):
            # If user is not authenticated, block access to harmful content
            if not self.request.user.is_authenticated:
                if (
                    posts.harmful_material_categories.exists()
                    or posts.harmful_tool_categories.exists()
                ):
                    raise PermissionDenied(
                        "You are not allowed to access this post."
                    )
                return posts
            # If authenticated, check the user's profile and age
            if not self.check_maturity():
                if (
                    posts.harmful_material_categories.exists()
                    or posts.harmful_tool_categories.exists()
                ):
                    raise PermissionDenied(
                        "You are not allowed to access this post."
                    )
                return posts

            # If user is mature, allow access
            return posts

        # If the user is a guest
        if not self.request.user.is_authenticated:
            # Only return posts without harmful material categories and tools
            return posts.filter(
                harmful_material_categories__isnull=True,
                harmful_tool_categories__isnull=True,
            )

        # if authenticated, filter out age restricted content
        if not self.check_maturity():
            # Return posts without harmful material and tool categories
            return posts.filter(
                harmful_material_categories__isnull=True,
                harmful_tool_categories__isnull=True,
            )

        # If the user is mature, return all posts
        return posts

    def filter_posts(self, filters):
        """
        Filters posts based on the filters provided in JSON.
        """
        posts = self.filter_age_restricted_content(Post.objects.all())

        # Apply filters dynamically
        user_id = filters.get("user_id")  # Could be ID or username
        search_query = filters.get("search_query", [])

        if user_id:
            if str(user_id).isdigit():
                # Filter by user ID if it's numeric
                posts = posts.filter(user__id=user_id)
            else:
                # Filter by username (case-insensitive)
                posts = posts.filter(user__username__iexact=user_id)
        if search_query:
            for term in search_query:
                posts = posts.filter(
                    Q(title__icontains=term) | Q(description__icontains=term)
                )

        return posts


class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            try:
                post = Post.objects.get(id=post_id)
            except Post.DoesNotExist:
                return throw_error(
                    404,
                    "Post doesn't exist.",
                    log="User tried to like a post that doesn't exist.",
                )
            # Check if the like already exists
            if Like.objects.filter(post=post, user=request.user).exists():
                return throw_error(
                    400,
                    "You have already liked this post",
                    log="Rejected user who tried to like an already "
                    + "liked post.",
                )
            # Create the like
            like = Like.objects.create(post=post, user=request.user)
            return Response(
                {"message": "Post liked successfully!", "id": like.id},
                status=201,
            )
        except Exception as e:
            return throw_error(500, "Unable to like post.", log=str(e))

    def delete(self, request, post_id):
        try:
            like = Like.objects.filter(
                post_id=post_id, user=request.user
            ).first()
            if like:
                like.delete()
                return Response(
                    {
                        "message": "Like removed successfully!",
                        "post_id": post_id,
                    },
                    status=200,
                )
            return throw_error(
                500,
                "Couldn't find like, nothing to remove.",
                log="Rejected user who tried to remove a like that "
                + "doens't exist.",
            )
        except Exception as e:
            return throw_error(500, "Unable to remove like.", log=str(e))
