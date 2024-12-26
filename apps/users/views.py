from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Profile as ProfileModel
from .serializers import ProfileSerializer
from static.py.utils import throw_error


class Profile(APIView):
    """Returns a profile based on the primary key"""
    http_method_names = ['get']  # Only allow get requests

    def get(self, request, pk):
        try:
            profile = ProfileModel.objects.get(user__id=pk)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data, status=200)
        except ProfileModel.DoesNotExist:
            return throw_error(
                404,
                "Profile not found.",
                log=f"Profile not found for user ID: {pk}"
            )
        except Exception as e:
            return throw_error(
                500,
                "Something went wrong.",
                log=f"Unhandled exception: {str(e)}"
            )
