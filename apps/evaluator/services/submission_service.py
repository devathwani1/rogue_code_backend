import ast

from django.utils import timezone

from apps.challenges.models import UserQuestionLastAttempt
from apps.challenges.models.questions import Question
from apps.challenges.services.daily_progress_service import DailyProgressService
from apps.evaluator.services.code_validators import CodeValidator
from apps.evaluator.services.runner import run_code
from apps.evaluator.services.validators_java_cpp import (
    validate_cpp_submission,
    validate_java_submission,
)


class SubmissionService:

    @staticmethod
    def evaluate(code: str, question_id, language: str = "python", user=None) -> dict:
        question = Question.objects.get(id=question_id)
        lang = (language or "python").lower()
        if lang not in ("python", "java", "cpp"):
            raise ValueError(f"Unsupported language: {language}")

        if lang == "python":
            tree = ast.parse(code)
            CodeValidator(question).validate(tree)
        elif lang == "java":
            validate_java_submission(code, question)
        else:
            validate_cpp_submission(code, question)

        results = run_code(code, question, lang)

        all_cases = list(question.test_cases.all())
        results = list(results)
        if len(results) < len(all_cases):
            results.extend([False] * (len(all_cases) - len(results)))
        elif len(results) > len(all_cases):
            results = results[: len(all_cases)]

        passed = sum(1 for r in results if r)
        total = len(results)

        success = passed == total

        # Align with API public test_cases: map by pk to runner index
        by_pk = {tc.pk: bool(results[i]) for i, tc in enumerate(all_cases)}
        public_cases = list(question.test_cases.filter(is_hidden=False))
        case_results = [by_pk.get(tc.pk, False) for tc in public_cases]

        # Persist day-wise progress when the request is authenticated.
        if user is not None:
            UserQuestionLastAttempt.objects.update_or_create(
                user=user,
                question=question,
                defaults={
                    "last_attempted_at": timezone.now(),
                    "last_success": success,
                    "last_passed": passed,
                    "last_total": total,
                },
            )
            DailyProgressService.record_question_solve(
                user,
                question_id=question_id,
                passed=passed,
                total=total,
                success=success,
            )
            DailyProgressService.recompute_profile_progress(user)

        return {
            "passed": passed,
            "total": total,
            "success": success,
            "case_results": case_results,
        }
