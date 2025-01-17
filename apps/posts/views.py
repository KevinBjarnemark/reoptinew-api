from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from static.py.utils.error_handling import throw_error
from static.py.utils.logging import log_debug
from .serializers import PostSerializer
from .models import Post


class PostAPIView(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        show_debugging = True
        try:
            posts = Post.objects.all()
            serializer = PostSerializer(
                posts, many=True, context={'request': request}
            )

            log_debug(
                show_debugging,
                "Returning all posts to the client.",
                serializer.data,
            )
            return Response(serializer.data, status=200)
        except Exception as e:
            return throw_error(500, "Unable to load posts.", log=str(e))

    def post(self, request):
        try:
            serializer = PostSerializer(
                data=request.data, context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return throw_error(
                400,
                "Validation failed.",
                log=serializer.errors,
                error_details=serializer.errors,
            )
        except Exception as e:
            return throw_error(500, "Unable to create post.", log=str(e))
