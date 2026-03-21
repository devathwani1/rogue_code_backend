"""Language used for solve-page starter code and evaluation (matches user profile)."""


def get_solve_language(request) -> str:
    language = "python"
    if request and getattr(request, "user", None) and request.user.is_authenticated:
        try:
            language = request.user.profile.language or "python"
        except Exception:
            pass
    if language not in ("python", "java", "cpp"):
        language = "python"
    return language
