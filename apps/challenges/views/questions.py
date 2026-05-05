from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
import json

from apps.challenges.models import Question, UserQuestionLastAttempt
from apps.challenges.serializers.recent_attempts import UserQuestionLastAttemptSerializer
from apps.challenges.services.question_service import QuestionService
from apps.challenges.serializers.questions import QuestionSerializer, QuestionSolveSerializer
from apps.common.utils import Utils


def _normalize_question_payload(request):
    """
    Supports multipart/form-data admin uploads where structured fields are JSON strings.
    """
    # request.data is often a QueryDict for multipart requests; assigning dict/list
    # values back into QueryDict coerces them to strings. Build a plain dict instead.
    data = {k: request.data.get(k) for k in request.data.keys()}
    if "image" in request.FILES:
        data["image"] = request.FILES["image"]

    for key in ("return_type", "parameters", "test_cases"):
        val = data.get(key)
        if isinstance(val, str):
            data[key] = json.loads(val)
    return data

class RecentQuestionAttemptsView(APIView):
    """
    GET ?q=5 — most recently submitted questions for the current user (default 10, max 50).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        raw = request.query_params.get("q")
        if raw is None or str(raw).strip() == "":
            limit = 10
        else:
            try:
                limit = int(raw)
            except (TypeError, ValueError):
                return Response(
                    data=Utils.error_response_data(
                        message="Invalid query",
                        error=["Query parameter 'q' must be a positive integer."],
                    ),
                    status=status.HTTP_400_BAD_REQUEST,
                )
        limit = max(1, min(limit, 50))

        qs = (
            UserQuestionLastAttempt.objects.filter(user=request.user)
            .select_related("question")
            .order_by("-last_attempted_at")[:limit]
        )
        serializer = UserQuestionLastAttemptSerializer(qs, many=True)
        return Response(
            Utils.success_response_data(
                message="Recent question attempts retrieved successfully",
                data=serializer.data,
            )
        )


class AdminQuestionListView(APIView):
    """Staff-only: all questions + total count (for admin dashboard)."""

    permission_classes = [IsAdminUser]

    def get(self, request):
        qs = Question.objects.all().order_by("-created_at")
        count = qs.count()
        serializer = QuestionSerializer(qs, many=True)
        return Response(
            Utils.success_response_data(
                message="Admin questions retrieved successfully",
                data={"count": count, "questions": serializer.data},
            )
        )


class QuestionListView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return []

    def get(self, request):
        questions = QuestionService.list_questions()
        serializer = QuestionSerializer(questions, many=True)
        return Response(Utils.success_response_data(
            message="Questions retrieved successfully",
            data=serializer.data
        ))

    def post(self, request):
        payload = _normalize_question_payload(request)
        question = QuestionService.create_question(
            payload, context={"request": request}
        )
        return Response(
            status=status.HTTP_201_CREATED,
            data=Utils.success_response_data(
                message="Question created successfully",
                data=QuestionSerializer(question).data
            )
        )

class QuestionDetailView(APIView):
    def get_permissions(self):
        if self.request.method in ("PATCH", "PUT", "DELETE"):
            return [IsAdminUser()]
        return []

    def get(self, request, question_id):
        question = QuestionService.get_question_by_id(question_id)
        if not question:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data=Utils.error_response_data(
                    message="Question not found",
                    error=["The requested question does not exist"]
                )
            )
        
        serializer = QuestionSerializer(question)
        return Response(Utils.success_response_data(
            message="Question retrieved successfully",
            data=serializer.data
        ))

    def patch(self, request, question_id):
        question = QuestionService.get_question_by_id(question_id)
        if not question:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data=Utils.error_response_data(
                    message="Question not found",
                    error=["The requested question does not exist"],
                ),
            )
        serializer = QuestionSerializer(
            question,
            data=_normalize_question_payload(request),
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            Utils.success_response_data(
                message="Question updated successfully",
                data=serializer.data,
            )
        )

    def delete(self, request, question_id):
        question = QuestionService.get_question_by_id(question_id)
        if not question:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data=Utils.error_response_data(
                    message="Question not found",
                    error=["The requested question does not exist"],
                ),
            )
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class QuestionSolveView(APIView):
    def get(self, request, question_id):
        question = QuestionService.get_question_by_id(question_id)
        if not question:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data=Utils.error_response_data(
                    message="Question not found",
                    error=["The requested question does not exist"]
                )
            )
        
        serializer = QuestionSolveSerializer(question, context={'request': request})
        return Response(Utils.success_response_data(
            message="Question solving data retrieved successfully",
            data=serializer.data
        ))
