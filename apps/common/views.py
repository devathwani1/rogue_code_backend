from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Difficulty
from .serializers import DifficultySerializer
from .utils import Utils

class DifficultyListView(APIView):
    authentication_classes = [] 
    permission_classes = []      # Allow public access to difficulties

    def get(self, request):
        difficulties = Difficulty.objects.all().order_by('id')
        serializer = DifficultySerializer(difficulties, many=True)
        return Response(Utils.success_response_data(
            message="Difficulties retrieved successfully",
            data=serializer.data
        ), status=status.HTTP_200_OK)
