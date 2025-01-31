from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    AllowAny,
    IsAuthenticated,
)
from django.db.models import Q
from static.utils.error_handling import throw_error
from static.utils.logging import log_debug
from static.utils.helpers import check_age
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

            # Return all posts
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

        except Exception:
            return age_restricted_error()

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

            def is_harmful():
                """
                Helper function to check if a post contains
                harmful content.
                """
                harmful_material = data.get(
                    "harmful_material_categories", None
                )
                harmful_tools = data.get("harmful_tool_categories", None)
                harmful_post = data.get("harmful_post", "false")

                # Ensure correct boolean conversion
                harmful_material = bool(
                    harmful_material
                    and harmful_material not in ["[]", [], None]
                )
                harmful_tools = bool(
                    harmful_tools and harmful_tools not in ["[]", [], None]
                )
                harmful_post = str(harmful_post).lower() in ["true", "1"]
                return harmful_material or harmful_tools or harmful_post

            # User is not mature enough to create this post
            if not self.user_is_mature() and is_harmful():
                log_debug(
                    show_debugging,
                    "User is not old enough to create post "
                    + "because it contains harmful content.",
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
                return throw_error(
                    400,
                    "Post ID is required for updates.",
                    log="pk not included in the update post request.",
                )

            # Fetch the post
            try:
                post = Post.objects.get(pk=pk)
            except Post.DoesNotExist:
                return throw_error(
                    404,
                    "Post not found.",
                    log="User wanted to fetch a post that doens't exist.",
                )

            # User must be the owner of the post
            if post.user != request.user:
                return throw_error(
                    403,
                    "You are not allowed to edit this post.",
                    log="User is not the owner of the post.",
                )

            # Request body (mutable copy)
            data = request.data.copy()
            # Convert stringified FormData (js)
            convert_str_to_complex_obj(
                show_debugging, data, ["tools", "materials"]
            )

            # Return an error if the user is not mature enough to create post
            if not self.user_is_mature():
                log_debug(
                    show_debugging,
                    "User is not old enough to update this post "
                    + "because it contains harmful content.",
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

    def user_is_mature(self):
        """
        Returns `True` if the user is mature and older than the
        AGE_RESTRICTED_CONTENT_AGE constant variable, `False` otherwise.
        """
        show_debugging = True

        # User is a guest and assumed to not be mature
        if not self.request.user.is_authenticated:
            log_debug(
                show_debugging,
                "User is assumed to be immature because they're "
                + "not authenticated",
                "",
            )
            return False
        # Return False is user has no profile
        profile = getattr(self.request.user, "profile", None)
        if not profile:
            log_debug(
                show_debugging,
                "Checking is user is mature but profile is missing.",
                "",
            )
            return False

        # Check user's age
        user_age = check_age(profile.birth_date)
        age_restriction = GLOBAL_VALIDATION_RULES["AGE_RESTRICTED_CONTENT_AGE"]
        # User is not mature
        if user_age <= age_restriction:
            log_debug(
                show_debugging,
                f"User is {user_age} old and the age restriction "
                + f"is {age_restriction} so user is NOT mature.",
                "",
            )
            return False

        log_debug(
            show_debugging,
            f"User is {user_age} old and the age restriction "
            + f"is {age_restriction} so user is mature.",
            "",
        )
        return True

    def filter_age_restricted_content(self, posts):
        """
        Filters posts based on the user's authentication and maturity.
        Guests and users under 16 can only see safe posts.
        """
        show_debugging = True

        def is_harmful(posts):
            """Helper function to check if a post contains
            harmful content."""
            return (
                (
                    getattr(posts, "harmful_material_categories", None)
                    and posts.harmful_material_categories.exists()
                )
                or (
                    getattr(posts, "harmful_tool_categories", None)
                    and posts.harmful_tool_categories.exists()
                )
                or bool(
                    getattr(
                        posts,
                        "harmful_post",
                    )
                )
            )

        # Handle single instance (not a queryset)
        if isinstance(posts, Post):
            log_debug(
                show_debugging,
                "User requests a single post",
                "",
            )
            # The user is a guest, filter out harmful content
            if not self.request.user.is_authenticated:
                log_debug(
                    show_debugging,
                    "User is a guest, will return a safe post",
                    "",
                )
                if is_harmful(posts):
                    raise Exception("Age restriceted content")
                return posts
            if not self.user_is_mature():
                log_debug(
                    show_debugging,
                    "User is authenticated but not mature, returning "
                    + "a safe post",
                    "",
                )
                if is_harmful(posts):
                    raise Exception("Age restriceted content")
                return posts
            # User authenticated and mature, allow acces to all posts
            return posts

        # If it's a queryset (multiple posts)
        # The user is a guest, filter out harmful content
        if not self.request.user.is_authenticated:
            log_debug(
                show_debugging,
                "User is not authenticated, showing only safe posts.",
                "",
            )
            return posts.filter(
                harmful_material_categories__isnull=True,
                harmful_tool_categories__isnull=True,
                harmful_post=False,
            )
        # Authenticated but not mature
        if not self.user_is_mature():
            log_debug(
                show_debugging,
                "User is not mature enough to post this post "
                + "because harmful content was found in it.",
                "",
            )
            return posts.filter(
                harmful_material_categories__isnull=True,
                harmful_tool_categories__isnull=True,
                harmful_post=False,
            )
        # User is authenticated and mature, return all posts
        log_debug(
            show_debugging,
            "Returning all posts because the user is authenticated "
            + "and mature."
            "",
        )
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


class DeletePostView(APIView):
    """
    Deletes a user's account.
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request, pk=None):
        show_debugging = True
        try:
            log_debug(
                show_debugging,
                f"DELETE request! (posts) post id: {pk}",
                "",
            )
            # Fetch the post
            try:
                post = Post.objects.get(pk=pk)
            except Post.DoesNotExist:
                return throw_error(
                    404,
                    "Post not found.",
                    log="User tried to delete a post that doens't exist.",
                )

            # User must be the owner of the post
            if post.user != request.user:
                return throw_error(
                    403,
                    "You are not allowed to delete this post.",
                    log="User tried to delete a post, but they are "
                    + "not the owner of it, rejected.",
                )

            # Delete the post
            post.delete()

            # Return a successful response
            return Response(
                {
                    "message": "Deleted post successfully.",
                },
                status=200,
            )
        # Handle unexpected errors
        except Exception as e:
            return throw_error(
                500,
                "Something went wrong during post deletion.",
                log=f"Unhandled exception: {str(e)}",
            )
