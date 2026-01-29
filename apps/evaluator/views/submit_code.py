# views/submit.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from serializers.submit import SubmitCodeSerializer
from services.submission_service import SubmissionService

class SubmitSolutionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SubmitCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = SubmissionService.evaluate(
            serializer.validated_data["code"],
            serializer.validated_data["question_id"]
        )

        return Response(result)
