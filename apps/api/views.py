from rest_framework.views import APIView
from rest_framework.response import Response


class ApiView(APIView):
    def get(self, request):
        return Response({"Test": "Hello"})
