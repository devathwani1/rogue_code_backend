"""Lightweight static checks for Java / C++ submissions (no AST)."""
from __future__ import annotations

import re


JAVA_DENY = (
    "ProcessBuilder",
    "Runtime.getRuntime",
    "java.lang.reflect",
    "ClassLoader",
    "SecurityManager",
    "System.load",
    "System.loadLibrary",
)

CPP_DENY_PATTERNS = (
    r"\bsystem\s*\(",
    r"\bpopen\s*\(",
    r"\bfork\s*\(",
    r"\bexecl\s*\(",
    r"\bexeclp\s*\(",
    r"\bexecv\s*\(",
    r"\bexecvp\s*\(",
)


def validate_java_submission(code: str, question) -> None:
    if not code or not code.strip():
        raise ValueError("Empty submission")

    if re.search(r"^\s*package\s+", code, re.MULTILINE):
        raise ValueError("Do not use a 'package' declaration; use the default package.")

    if "class Solution" not in code:
        raise ValueError("Submission must contain 'class Solution'.")

    fn = question.function_name
    if not re.search(rf"\b{re.escape(fn)}\s*\(", code):
        raise ValueError(f"Method '{fn}' not found in submission.")

    upper = code
    for token in JAVA_DENY:
        if token in upper:
            raise ValueError(f"Disallowed construct: {token}")


def validate_cpp_submission(code: str, question) -> None:
    if not code or not code.strip():
        raise ValueError("Empty submission")

    if "class Solution" not in code:
        raise ValueError("Submission must contain 'class Solution'.")

    fn = question.function_name
    if not re.search(rf"\b{re.escape(fn)}\s*\(", code):
        raise ValueError(f"Method '{fn}' not found in submission.")

    if re.search(r"\bint\s+main\s*\(", code):
        raise ValueError("Do not define main(); the judge adds it.")

    for pat in CPP_DENY_PATTERNS:
        if re.search(pat, code):
            raise ValueError(f"Disallowed construct matches pattern: {pat}")
