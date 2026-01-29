from apps.evaluator.services.runner import run_code
from apps.evaluator.services.code_validators import CodeValidator
import ast
from apps.challenges.models.questions import Question

class SubmissionService:

    @staticmethod
    def evaluate(code, question_slug):
        question = Question.get(slug=question_slug)
        tree = ast.parse(code)
        CodeValidator(question).validate(tree)

        results = run_code(code, question)

        passed = sum(results)
        total = len(results)

        return {
            "passed": passed,
            "total": total,
            "success": passed == total
        }
