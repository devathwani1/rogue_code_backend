"""
Build Java / C++ source literals from JSON test values using the same TypeSchema as the rest of the project.
"""
from __future__ import annotations

from apps.compiler.services.cpp_mapper import CppMapper


def _java_escape_string(s: str) -> str:
    out = []
    for ch in s:
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        else:
            out.append(ch)
    return "".join(out)


def java_literal(value, schema: dict) -> str:
    if not schema or not isinstance(schema, dict):
        raise ValueError("Invalid type schema for Java literal")

    kind = schema.get("kind")

    if kind == "primitive":
        name = schema.get("name")
        if name == "int":
            return str(int(value))
        if name == "bool":
            return "true" if bool(value) else "false"
        if name == "string":
            return '"' + _java_escape_string(str(value)) + '"'
        raise ValueError(f"Unsupported primitive for Java literal: {name}")

    if kind == "array":
        of = schema.get("of") or {}
        if not isinstance(value, (list, tuple)):
            raise ValueError("Expected JSON array for array type")
        parts = [java_literal(v, of) for v in value]
        joined = ", ".join(parts)
        return f"new java.util.ArrayList<>(java.util.Arrays.asList({joined}))"

    if kind == "map":
        key_s = schema.get("key") or {}
        val_s = schema.get("value") or {}
        if not isinstance(value, dict):
            raise ValueError("Expected JSON object for map type")
        lines = ["new java.util.HashMap<>() {{"]
        for k, v in value.items():
            lines.append(
                f"  put({java_literal(k, key_s)}, {java_literal(v, val_s)});"
            )
        lines.append("}}")
        return "\n".join(lines)

    if kind == "linked_list":
        from apps.evaluator.services.linked_list_literals import java_listnode_literal

        return java_listnode_literal(value, schema)

    raise ValueError(f"Unsupported schema kind for Java literal: {kind}")


def _cpp_escape_string(s: str) -> str:
    out = ['"']
    for ch in s:
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def cpp_literal(value, schema: dict) -> str:
    if not schema or not isinstance(schema, dict):
        raise ValueError("Invalid type schema for C++ literal")

    kind = schema.get("kind")

    if kind == "primitive":
        name = schema.get("name")
        if name == "int":
            return str(int(value))
        if name == "bool":
            return "true" if bool(value) else "false"
        if name == "string":
            return _cpp_escape_string(str(value))
        raise ValueError(f"Unsupported primitive for C++ literal: {name}")

    if kind == "array":
        of = schema.get("of") or {}
        if not isinstance(value, (list, tuple)):
            raise ValueError("Expected JSON array for array type")
        inner_type = CppMapper.to_cpp_type(of)
        elems = ", ".join(cpp_literal(v, of) for v in value)
        return f"vector<{inner_type}>{{{elems}}}"

    if kind == "map":
        key_s = schema.get("key") or {}
        val_s = schema.get("value") or {}
        kt = CppMapper.to_cpp_type(key_s)
        vt = CppMapper.to_cpp_type(val_s)
        if not isinstance(value, dict):
            raise ValueError("Expected JSON object for map type")
        pairs = ", ".join(
            f"{{{cpp_literal(k, key_s)}, {cpp_literal(v, val_s)}}}"
            for k, v in value.items()
        )
        return f"unordered_map<{kt}, {vt}>{{{pairs}}}"

    if kind == "linked_list":
        from apps.evaluator.services.linked_list_literals import cpp_listnode_literal

        return cpp_listnode_literal(value, schema)

    raise ValueError(f"Unsupported schema kind for C++ literal: {kind}")


def java_expected_literal(value, return_schema: dict) -> str:
    """Expected value literal (same as argument literals for supported types)."""
    return java_literal(value, return_schema)


def cpp_expected_literal(value, return_schema: dict) -> str:
    return cpp_literal(value, return_schema)
