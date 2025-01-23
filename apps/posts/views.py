import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from static.py.utils.error_handling import throw_error
from static.py.utils.logging import log_debug
from static.py.utils.helpers import user_is_mature
from apps.users.constants import VALIDATION_RULES
from .serializers import PostSerializer
from .models import Post


class PostAPIView(APIView):
    # Override permissions for specific actions
    def get_permissions(self):
        if self.request.method == 'POST':
            action = self.request.data.get('action', 'create')
            if action == 'filter':
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
        try:
            if pk:
                # Single post request
                single_post = self.filter_age_restricted_content(
                    Post.objects.get(pk=pk)
                )

                serializer = PostSerializer(
                    single_post, context={'request': request}
                )
                log_debug(
                    show_debugging,
                    "Returning single post to the client.",
                    serializer.data,
                )
                return Response(serializer.data, status=200)

            # List all posts
            posts = self.filter_age_restricted_content(Post.objects.all())
            serializer = PostSerializer(
                posts, many=True, context={'request': request}
            )

            log_debug(
                show_debugging,
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
                    + f"{VALIDATION_RULES['AGE_RESTRICTED_CONTENT_AGE']} "
                    + "years old to view this post."
                },
                status=403,
            )

    def post(self, request):
        try:
            # Request type
            action = request.data.get('action', 'create')

            # Handle search/filter action
            if action == 'filter':
                try:
                    filters = request.data.get('filters', {})
                    posts = self.filter_posts(filters)
                    serializer = PostSerializer(
                        posts,
                        many=True,
                        context={'request': request},
                    )
                    return Response(serializer.data, status=200)
                except Exception as e:
                    return throw_error(
                        500, "Unable to filter posts.", log=str(e)
                    )

            # Handle post creation
            # Request body mutable copy
            data = request.data.copy()

            # Convert FormData (JavaScript) to lists
            if "tools" in data:
                # Convert JSON string to list
                data["tools"] = json.loads(data["tools"])

            if "materials" in data:
                # Convert JSON string to list
                data["materials"] = json.loads(data["materials"])

            # Return an error if the user is not mature enough to create post
            if not self.check_maturity():
                return throw_error(
                    400,
                    "You must be at least "
                    + str(VALIDATION_RULES['AGE_RESTRICTED_CONTENT_AGE'])
                    + " years old to create a post that contain harmful "
                    + "tools and materials.",
                    log="Blocked a user from creating a post because the"
                    + " user is not old enough.",
                )

            serializer = PostSerializer(
                data=data, context={'request': request}
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

    def check_maturity(self):
        """
        Returns True if the user is older than the
        AGE_RESTRICTED_CONTENT_AGE constant variable, False otherwise.
        """
        profile = getattr(self.request.user, 'profile', None)
        if not user_is_mature(
            profile.birth_date,
            VALIDATION_RULES["AGE_RESTRICTED_CONTENT_AGE"],
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
                    posts.harmful_materials.exists()
                    or posts.harmful_tools.exists()
                ):
                    raise PermissionDenied(
                        "You are not allowed to access this post."
                    )
                return posts
            # If authenticated, check the user's profile and age
            if not self.check_maturity():
                if (
                    posts.harmful_materials.exists()
                    or posts.harmful_tools.exists()
                ):
                    raise PermissionDenied(
                        "You are not allowed to access this post."
                    )
                return posts

            # If user is mature, allow access
            return posts

        # If the user is a guest
        if not self.request.user.is_authenticated:
            # Only return posts without harmful materials and tools
            return posts.filter(
                harmful_materials__isnull=True,
                harmful_tools__isnull=True,
            )

        # if authenticated, filter out age restricted content
        if not self.check_maturity():
            # Return posts without harmful materials and tools
            return posts.filter(
                harmful_materials__isnull=True,
                harmful_tools__isnull=True,
            )

        # If the user is mature, return all posts
        return posts

    def filter_posts(self, filters):
        """
        Filters posts based on the filters provided in JSON.
        """
        posts = self.filter_age_restricted_content(Post.objects.all())

        # Apply filters dynamically
        user_id = filters.get('user_id')  # Could be ID or username
        search_query = filters.get('search_query', [])

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
