from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.challenges.services.question_service import QuestionService
from apps.challenges.serializers.questions import QuestionSerializer
from apps.common.utils import Utils

class QuestionListView(APIView):
    def get(self, request):
        questions = QuestionService.list_active_questions()
        serializer = QuestionSerializer(questions, many=True)
        return Response(Utils.success_response_data(
            message="Questions retrieved successfully",
            data=serializer.data
        ))

    def post(self, request):
        serializer = QuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = QuestionService.create_question(serializer.validated_data)
        return Response(
            status=status.HTTP_201_CREATED,
            data=Utils.success_response_data(
                message="Question created successfully",
                data=QuestionSerializer(question).data
            )
        )

class QuestionDetailView(APIView):
    def get(self, request, slug):
        question = QuestionService.get_question_by_slug(slug)
        if not question:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data=Utils.error_response_data(
                    message="Question not found",
                    error=["The requested question does not exist or is inactive"]
                )
            )
        
        serializer = QuestionSerializer(question)
        return Response(Utils.success_response_data(
            message="Question retrieved successfully",
            data=serializer.data
        ))
