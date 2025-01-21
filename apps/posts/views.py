from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django.db.models import Q
from static.py.utils.error_handling import throw_error
from static.py.utils.logging import log_debug
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

    def get(self, request):
        show_debugging = True
        try:
            posts = Post.objects.all()
            serializer = PostSerializer(
                posts, many=True, context={'request': request}
            )

            log_debug(
                show_debugging,
                "Returning post(s) to the client.",
                serializer.data,
            )
            return Response(serializer.data, status=200)
        except Exception as e:
            return throw_error(500, "Unable to load posts.", log=str(e))

    def post(self, request):
        try:
            action = request.data.get('action', 'create')

            # Handle search/filter action
            if action == 'filter':
                try:
                    filters = request.data.get('filters', {})
                    queryset = self.filter_posts(filters)
                    serializer = PostSerializer(
                        queryset, many=True, context={'request': request}
                    )
                    return Response(serializer.data, status=200)
                except Exception as e:
                    return throw_error(
                        500, "Unable to filter posts.", log=str(e)
                    )

            # Default: Handle post creation
            serializer = PostSerializer(
                data=request.data, context={'request': request}
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

    def filter_posts(self, filters):
        """
        Filters posts based on the filters provided in JSON.
        """
        queryset = Post.objects.all()

        # Apply filters dynamically
        user_id = filters.get('user_id')  # Could be ID or username
        search_query = filters.get('search_query', [])

        if user_id:
            if str(user_id).isdigit():
                # Filter by user ID if it's numeric
                queryset = queryset.filter(user__id=user_id)
            else:
                # Filter by username (case-insensitive)
                queryset = queryset.filter(user__username__iexact=user_id)
        if search_query:
            for term in search_query:
                queryset = queryset.filter(
                    Q(title__icontains=term) | Q(description__icontains=term)
                )

        return queryset


class SinglePost(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        show_debugging = True
        try:
            single_post = Post.objects.get(pk=pk)
            serializer = PostSerializer(
                single_post, context={'request': request}
            )

            log_debug(
                show_debugging,
                "Returning post to the client.",
                serializer.data,
            )
            return Response(serializer.data, status=200)
        except Exception as e:
            return throw_error(500, "Unable to load posts.", log=str(e))
