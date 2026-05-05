"""
Compile and run C++ submissions with g++ -std=c++17.
User code (class Solution { ... }) is embedded before a generated main().
"""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
import shutil
import signal

from apps.compiler.services.cpp_mapper import CppMapper
from apps.evaluator.services.linked_list_literals import schema_is_linked_list
from apps.evaluator.services.source_literals import cpp_literal


def _cpp_expected_expr(value, return_schema: dict) -> str:
    return cpp_literal(value, return_schema)


def _build_main_cpp(user_code: str, question) -> str:
    params = list(question.parameters.all().order_by("order"))
    ret_schema = question.return_type or {}
    needs_linked_list = schema_is_linked_list(ret_schema)

    parts = []
    parts.append(user_code.strip())
    parts.append("")
    if needs_linked_list:
        parts.append("bool listEquals(ListNode *a, ListNode *b) {")
        parts.append("    while (a && b) {")
        parts.append("        if (a->val != b->val) return false;")
        parts.append("        a = a->next;")
        parts.append("        b = b->next;")
        parts.append("    }")
        parts.append("    return !a && !b;")
        parts.append("}")
        parts.append("")
    parts.append("int main() {")
    parts.append("    Solution sol;")

    cases = list(question.test_cases.all())
    parts.append(f"    bool r[{len(cases)}];")

    for idx, tc in enumerate(cases):
        input_data = tc.input_data
        if not isinstance(input_data, (list, tuple)):
            input_data = [input_data]
        if len(input_data) != len(params):
            raise ValueError(
                f"Test case {idx}: expected {len(params)} inputs, got {len(input_data)}"
            )

        for p_i, p in enumerate(params):
            lit = cpp_literal(input_data[p_i], p.type_schema)
            ctype = CppMapper.to_cpp_type(p.type_schema)
            parts.append(f"    {ctype} p{idx}_{p_i} = {lit};")

        arg_list = ", ".join(f"p{idx}_{j}" for j in range(len(params)))
        exp = _cpp_expected_expr(tc.expected_output, ret_schema)
        ret_t = CppMapper.to_cpp_type(ret_schema)
        if schema_is_linked_list(ret_schema):
            parts.append(
                f"    {{ {ret_t} __a = sol.{question.function_name}({arg_list}); "
                f"{ret_t} __e = {exp}; "
                f"r[{idx}] = listEquals(__a, __e); }}"
            )
        else:
            parts.append(
                f"    {{ {ret_t} __a = sol.{question.function_name}({arg_list}); "
                f"{ret_t} __e = {exp}; "
                f"r[{idx}] = (__a == __e); }}"
            )

    parts.append("    std::cout << \"[\";")
    parts.append("    for (size_t i = 0; i < sizeof(r)/sizeof(r[0]); i++) {")
    parts.append("        if (i) std::cout << \",\";")
    parts.append("        std::cout << (r[i] ? \"true\" : \"false\");")
    parts.append("    }")
    parts.append("    std::cout << \"]\" << std::endl;")
    parts.append("    return 0;")
    parts.append("}")
    return "\n".join(parts)


def _parse_stdout_json(stdout: str):
    s = (stdout or "").strip()
    if not s:
        return None
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        lines = [ln.strip() for ln in s.splitlines() if ln.strip()]
        if lines:
            try:
                return json.loads(lines[-1])
            except json.JSONDecodeError:
                pass
        # Recovery path: user code may print extra text (e.g. debug logs)
        # before/around harness JSON. Try parsing from first JSON opener.
        for opener in ("[", "{"):
            i = s.find(opener)
            if i != -1:
                candidate = s[i:].strip()
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    continue
        return None
    return None


def run_cpp(user_code: str, question) -> list:
    user_code = user_code.strip()
    if not user_code:
        raise ValueError("Empty submission")

    if shutil.which("g++") is None:
        raise RuntimeError(
            "C++ compiler not found (need `g++`). Install build tools (e.g. `sudo apt-get install -y g++`)."
        )

    full_source = _build_main_cpp(user_code, question)
    header = """#include <iostream>
#include <vector>
#include <string>
#include <unordered_map>
#include <algorithm>

using namespace std;

"""

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        src_path = tmp_path / "submission.cpp"
        bin_path = tmp_path / "submission.out"
        src_path.write_text(header + full_source, encoding="utf-8")

        compile_proc = subprocess.run(
            [
                "g++",
                "-std=c++17",
                "-O2",
                "-pipe",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-Wno-unused-parameter",
                str(src_path),
                "-o",
                str(bin_path),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(tmp_path),
        )
        if compile_proc.returncode != 0:
            err = (compile_proc.stderr or compile_proc.stdout or "").strip()
            raise RuntimeError(f"C++ compile failed: {err or 'unknown error'}")

        run_proc = subprocess.run(
            [str(bin_path)],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(tmp_path),
        )

        out = (run_proc.stdout or "").strip()
        # If user code crashed/aborted, surface that first instead of generic JSON parse failure.
        if run_proc.returncode != 0:
            err = (run_proc.stderr or "").strip()
            rc = run_proc.returncode
            if rc < 0:
                sig = -rc
                sig_name = signal.Signals(sig).name if sig in signal.Signals._value2member_map_ else f"SIG{sig}"
                hint = ""
                if sig in (signal.SIGFPE, signal.SIGILL):
                    hint = " (possible arithmetic undefined behavior, e.g. division by zero)"
                elif sig == signal.SIGSEGV:
                    hint = " (segmentation fault / invalid memory access)"
                raise RuntimeError(
                    f"C++ runtime error: process terminated by signal {sig} ({sig_name}){hint}. "
                    f"stdout={out!r} stderr={err!r}"
                )
            raise RuntimeError(
                f"C++ runtime error: process exited with code {rc}. "
                f"stdout={out!r} stderr={err!r}"
            )
        parsed = _parse_stdout_json(out)
        if parsed is None:
            err = (run_proc.stderr or "").strip()
            raise RuntimeError(
                f"C++ produced no valid JSON. stdout={out!r} stderr={err!r} returncode={run_proc.returncode}"
            )
        if not isinstance(parsed, list):
            raise RuntimeError(f"Expected JSON array from harness, got {type(parsed)}")
        return [bool(x) for x in parsed]
