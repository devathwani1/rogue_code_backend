# services/runner.py
import subprocess
import tempfile
import json
import textwrap

def run_code(user_code, question):
    with tempfile.TemporaryDirectory() as tmp:
        code_path = f"{tmp}/solution.py"

        runner_code = textwrap.dedent(f"""
        {user_code}

        test_cases = {question.test_cases}

        results = []
        for inp, expected in test_cases:
            try:
                out = {question.function_name}(inp)
                results.append(out == expected)
            except Exception:
                results.append(False)

        print(json.dumps(results))
        """)

        with open(code_path, "w") as f:
            f.write(runner_code)

        result = subprocess.run(
            ["python", code_path],
            capture_output=True,
            text=True,
            timeout=2
        )

        return json.loads(result.stdout)
