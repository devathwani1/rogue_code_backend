# Multi-language runner dispatch
from __future__ import annotations

from apps.evaluator.services.python_runner import run_python
from apps.evaluator.services.java_runner import run_java
from apps.evaluator.services.cpp_runner import run_cpp


def run_code(user_code: str, question, language: str = "python") -> list:
    lang = (language or "python").lower()
    if lang == "python":
        return run_python(user_code, question)
    if lang == "java":
        return run_java(user_code, question)
    if lang == "cpp":
        return run_cpp(user_code, question)
    raise ValueError(f"Unsupported language: {language}")
