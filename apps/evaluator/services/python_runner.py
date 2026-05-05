# Python subprocess runner (user code + schema-aware harness)
import json
import subprocess
import tempfile
import textwrap


def _build_harness(question) -> str:
    """Build harness that converts JSON test values using parameter / return TypeSchema."""
    fn = question.function_name
    params = list(question.parameters.all().order_by("order"))
    param_schemas = [p.type_schema or {} for p in params]
    ret_schema = question.return_type or {}

    cases = []
    for tc in question.test_cases.all():
        inp = tc.input_data
        if not isinstance(inp, (list, tuple)):
            inp = [inp]
        cases.append((list(inp), tc.expected_output))

    schemas_json = repr(json.dumps(param_schemas))
    ret_json = repr(json.dumps(ret_schema))
    cases_repr = repr(cases)

    # ListNode is also prepended before user code so solutions can use one shared definition.
    body = """
import json

def _py_primitive(val, schema):
    name = schema.get("name")
    if name == "int":
        return int(val)
    if name == "bool":
        return bool(val)
    if name == "string":
        return str(val)
    raise ValueError("unsupported primitive")

def _json_to_value(val, schema):
    if not schema:
        return val
    kind = schema.get("kind")
    if kind == "primitive":
        return _py_primitive(val, schema)
    if kind == "linked_list":
        of = schema.get("of") or {"kind": "primitive", "name": "int"}
        if not isinstance(val, list):
            raise TypeError("linked_list input must be a JSON array")
        if not val:
            return None
        head = ListNode(_json_to_value(val[0], of))
        cur = head
        for x in val[1:]:
            cur.next = ListNode(_json_to_value(x, of))
            cur = cur.next
        return head
    if kind == "array":
        of = schema.get("of") or {}
        if not isinstance(val, list):
            raise TypeError("array expected")
        return [_json_to_value(v, of) for v in val]
    if kind == "map":
        ks = schema.get("key") or {}
        vs = schema.get("value") or {}
        if not isinstance(val, dict):
            raise TypeError("map expected")
        return {_json_to_value(k, ks): _json_to_value(v, vs) for k, v in val.items()}
    raise ValueError("unsupported input kind: " + str(kind))

def _value_to_json(val, schema):
    if not schema:
        return val
    kind = schema.get("kind")
    if kind == "primitive":
        return val
    if kind == "linked_list":
        out = []
        while val is not None:
            out.append(val.val)
            val = val.next
        return out
    if kind == "array":
        of = schema.get("of") or {}
        return [_value_to_json(v, of) for v in val]
    if kind == "map":
        ks = schema.get("key") or {}
        vs = schema.get("value") or {}
        return {_value_to_json(k, ks): _value_to_json(v, vs) for k, v in val.items()}
    raise ValueError("unsupported return kind: " + str(kind))

PARAM_SCHEMAS = json.loads(__SCHEMAS_JSON__)
RET_SCHEMA = json.loads(__RET_JSON__)
CASES = __CASES__

results = []
first_runtime_error = None
for case_idx, (inp, expected) in enumerate(CASES):
    try:
        args = [
            _json_to_value(inp[i], PARAM_SCHEMAS[i])
            for i in range(len(PARAM_SCHEMAS))
        ]
        out = __FN__(*args)
        got = _value_to_json(out, RET_SCHEMA)
        results.append(got == expected)
    except Exception as e:
        if first_runtime_error is None:
            first_runtime_error = f"case {case_idx + 1}: {type(e).__name__}: {e}"
        results.append(False)

print(json.dumps({"results": results, "runtime_error": first_runtime_error}))
"""
    body = body.replace("__SCHEMAS_JSON__", schemas_json)
    body = body.replace("__RET_JSON__", ret_json)
    body = body.replace("__CASES__", cases_repr)
    body = body.replace("__FN__", fn)
    return textwrap.dedent(body)


LISTNODE_STUB = textwrap.dedent(
    """
    class ListNode:
        __slots__ = ("val", "next")

        def __init__(self, val=0, next=None):
            self.val = val
            self.next = next

    """
).strip()


def run_python(user_code: str, question) -> list:
    harness = _build_harness(question)

    with tempfile.TemporaryDirectory() as tmp:
        code_path = f"{tmp}/solution.py"
        runner_code = LISTNODE_STUB + "\n\n" + user_code.strip() + "\n\n" + harness

        with open(code_path, "w") as f:
            f.write(runner_code)

        result = subprocess.run(
            ["python", code_path],
            capture_output=True,
            text=True,
            timeout=10,
        )

        stdout = (result.stdout or "").strip()
        if not stdout:
            stderr = (result.stderr or "").strip()
            raise RuntimeError(
                f"Code produced no output (returncode={result.returncode}). "
                f"stderr: {stderr or 'none'}"
            )
        try:
            parsed = json.loads(stdout)
            if isinstance(parsed, dict):
                runtime_error = parsed.get("runtime_error")
                results = parsed.get("results")
                if runtime_error:
                    raise RuntimeError(f"Python runtime error: {runtime_error}")
                if isinstance(results, list):
                    return results
            return parsed
        except json.JSONDecodeError:
            lines = [ln.strip() for ln in stdout.splitlines() if ln.strip()]
            if lines:
                try:
                    parsed = json.loads(lines[-1])
                    if isinstance(parsed, dict):
                        runtime_error = parsed.get("runtime_error")
                        results = parsed.get("results")
                        if runtime_error:
                            raise RuntimeError(f"Python runtime error: {runtime_error}")
                        if isinstance(results, list):
                            return results
                    return parsed
                except json.JSONDecodeError:
                    pass
            stderr = (result.stderr or "").strip()
            raise RuntimeError(
                f"Code did not print valid JSON. stdout: {result.stdout!r}. "
                f"stderr: {stderr or 'none'}"
            )
