# views/submit_code.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from apps.evaluator.seralizers.submit_code import SubmitCodeSerializer
from apps.evaluator.services.submission_service import SubmissionService


class SubmitSolutionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Log incoming payload for debugging 400s
        print("[Evaluator] Request data:", request.data)
        serializer = SubmitCodeSerializer(data=request.data)
        if not serializer.is_valid():
            print("[Evaluator] Validation errors:", serializer.errors)
            raise ValidationError(serializer.errors)

        try:
            result = SubmissionService.evaluate(
                serializer.validated_data["code"],
                serializer.validated_data["question_id"],
                serializer.validated_data.get("language") or "python",
                request.user,
            )
        except Exception as e:
            # Print evaluation error to Django (Python) console
            print("[Evaluator] Submission error:", e)
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Print evaluation result to Django (Python) console
        print("[Evaluator] Submission result:", result)
        return Response(result)
