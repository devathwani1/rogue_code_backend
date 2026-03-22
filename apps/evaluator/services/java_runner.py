"""
Compile and run Java submissions: user code in Solution.java, generated Harness.java runs tests.
"""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
import shutil

from apps.compiler.services.java_mapper import JavaMapper
from apps.evaluator.services.linked_list_literals import schema_is_linked_list
from apps.evaluator.services.source_literals import java_literal


def _java_expected_object_expr(value, return_schema: dict) -> str:
    kind = return_schema.get("kind")
    if kind == "primitive":
        name = return_schema.get("name")
        lit = java_literal(value, return_schema)
        if name == "int":
            return f"Integer.valueOf({lit})"
        if name == "bool":
            return f"Boolean.valueOf({lit})"
        if name == "string":
            return lit
    return java_literal(value, return_schema)


def _build_harness_source(question) -> str:
    params = list(question.parameters.all().order_by("order"))
    ret_schema = question.return_type or {}
    # ListNode lives in the user's Solution.java (java_mapper starter). Only the return path
    # calls linkedListEquals; omit the helper entirely for non-linked-list returns so Harness
    # compiles without referencing ListNode (fixes generic array/string problems).
    needs_linked_list = schema_is_linked_list(ret_schema)

    lines = [
        "import java.util.*;",
        "public class Harness {",
    ]
    if needs_linked_list:
        lines.extend(
            [
                "  static boolean linkedListEquals(ListNode a, ListNode b) {",
                "    while (a != null && b != null) {",
                "      if (a.val != b.val) return false;",
                "      a = a.next;",
                "      b = b.next;",
                "    }",
                "    return a == null && b == null;",
                "  }",
            ]
        )
    lines.extend(
        [
            "  public static void main(String[] args) {",
            "    Solution sol = new Solution();",
        ]
    )

    cases = list(question.test_cases.all())
    lines.append(f"    boolean[] r = new boolean[{len(cases)}];")

    for idx, tc in enumerate(cases):
        input_data = tc.input_data
        if not isinstance(input_data, (list, tuple)):
            input_data = [input_data]
        if len(input_data) != len(params):
            raise ValueError(
                f"Test case {idx}: expected {len(params)} inputs, got {len(input_data)}"
            )

        for p_i, p in enumerate(params):
            lit = java_literal(input_data[p_i], p.type_schema)
            jtype = JavaMapper.to_java_type(p.type_schema)
            lines.append(f"    {jtype} p{idx}_{p_i} = {lit};")

        arg_list = ", ".join(f"p{idx}_{j}" for j in range(len(params)))
        exp_expr = _java_expected_object_expr(tc.expected_output, ret_schema)

        lines.append(
            f"    Object __a{idx} = sol.{question.function_name}({arg_list});"
        )
        lines.append(f"    Object __e{idx} = {exp_expr};")
        if schema_is_linked_list(ret_schema):
            lines.append(
                f"    r[{idx}] = linkedListEquals((ListNode)__a{idx}, (ListNode)__e{idx});"
            )
        else:
            lines.append(
                f"    r[{idx}] = java.util.Objects.deepEquals(__a{idx}, __e{idx});"
            )

    lines.extend(
        [
            "    System.out.print(\"[\");",
            "    for (int i = 0; i < r.length; i++) {",
            "      if (i > 0) System.out.print(\",\");",
            "      System.out.print(r[i]);",
            "    }",
            "    System.out.println(\"]\");",
            "  }",
            "}",
        ]
    )
    return "\n".join(lines)


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
                return None
    return None


def run_java(user_code: str, question) -> list:
    user_code = user_code.strip()
    if not user_code:
        raise ValueError("Empty submission")

    if shutil.which("javac") is None or shutil.which("java") is None:
        raise RuntimeError(
            "Java runtime/compiler not found (need `javac` and `java`). "
            "Install an OpenJDK (e.g. `sudo apt-get install -y default-jdk`)."
        )

    harness = _build_harness_source(question)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        sol_path = tmp_path / "Solution.java"
        har_path = tmp_path / "Harness.java"
        sol_path.write_text(user_code, encoding="utf-8")
        har_path.write_text(harness, encoding="utf-8")

        compile_proc = subprocess.run(
            ["javac", str(sol_path), str(har_path)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(tmp_path),
        )
        if compile_proc.returncode != 0:
            err = (compile_proc.stderr or compile_proc.stdout or "").strip()
            raise RuntimeError(f"Java compile failed: {err or 'unknown error'}")

        run_proc = subprocess.run(
            ["java", "-cp", str(tmp_path), "Harness"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(tmp_path),
        )

        out = (run_proc.stdout or "").strip()
        parsed = _parse_stdout_json(out)
        if parsed is None:
            err = (run_proc.stderr or "").strip()
            raise RuntimeError(
                f"Java produced no valid JSON. stdout={out!r} stderr={err!r} returncode={run_proc.returncode}"
            )
        if not isinstance(parsed, list):
            raise RuntimeError(f"Expected JSON array from harness, got {type(parsed)}")
        return [bool(x) for x in parsed]
