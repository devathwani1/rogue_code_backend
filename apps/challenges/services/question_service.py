from multiprocessing import context
from apps.challenges.models import Question

class QuestionService:
    @staticmethod
    def list_questions():
        return Question.objects.all()

    @staticmethod
    def get_question_by_id(question_id):
        try:
            return Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return None

    @staticmethod
    def create_question(data, context):
        # We handle creation via Serializer now for nested objects
        from apps.challenges.serializers.questions import QuestionSerializer
        serializer = QuestionSerializer(data=data,
        context=context)
        serializer.is_valid(raise_exception=True)
        return serializer.save()
