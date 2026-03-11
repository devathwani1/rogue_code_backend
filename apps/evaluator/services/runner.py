# services/runner.py
import subprocess
import tempfile
import json
import textwrap


def run_code(user_code, question):
    # Build test cases as list of (input_list, expected) from question model
    test_cases_data = [
        (list(tc.input_data) if isinstance(tc.input_data, (list, tuple)) else [tc.input_data], tc.expected_output)
        for tc in question.test_cases.all()
    ]

    with tempfile.TemporaryDirectory() as tmp:
        code_path = f"{tmp}/solution.py"

        harness = textwrap.dedent(f"""
            import json
            test_cases = {test_cases_data!r}

            results = []
            for inp, expected in test_cases:
                try:
                    out = {question.function_name}(*inp)
                    results.append(out == expected)
                except Exception:
                    results.append(False)

            print(json.dumps(results))
        """)
        runner_code = user_code.strip() + "\n\n" + harness

        with open(code_path, "w") as f:
            f.write(runner_code)

        result = subprocess.run(
            ["python", code_path],
            capture_output=True,
            text=True,
            timeout=2
        )

        stdout = (result.stdout or "").strip()
        if not stdout:
            stderr = (result.stderr or "").strip()
            raise RuntimeError(
                f"Code produced no output (returncode={result.returncode}). "
                f"stderr: {stderr or 'none'}"
            )
        try:
            return json.loads(stdout)
        except json.JSONDecodeError:
            # Stray output (e.g. from user code or env) before our JSON; use last line
            lines = [ln.strip() for ln in stdout.splitlines() if ln.strip()]
            if lines:
                try:
                    return json.loads(lines[-1])
                except json.JSONDecodeError:
                    pass
            stderr = (result.stderr or "").strip()
            raise RuntimeError(
                f"Code did not print valid JSON. stdout: {result.stdout!r}. "
                f"stderr: {stderr or 'none'}"
            )
