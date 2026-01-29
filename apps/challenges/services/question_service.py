from apps.challenges.models.questions import Question

class QuestionService:
    @staticmethod
    def list_active_questions():
        return Question.objects.filter(is_active=True)

    @staticmethod
    def get_question_by_slug(slug):
        try:
            return Question.objects.get(slug=slug, is_active=True)
        except Question.DoesNotExist:
            return None

    @staticmethod
    def create_question(data):
        return Question.objects.create(**data)
