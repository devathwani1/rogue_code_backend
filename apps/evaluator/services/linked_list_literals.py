"""
JSON array <-> singly linked list literals for Java / C++ evaluators.

Test cases store linked lists as JSON arrays, e.g. [1, 2, 3].
`of` in the schema is the element type (typically primitive int).
"""
from __future__ import annotations

from apps.evaluator.services.source_literals import cpp_literal, java_literal


def java_listnode_literal(value, schema: dict) -> str:
    """value: JSON list -> nested `new ListNode(...)` (LeetCode-style API)."""
    of = schema.get("of") or {}
    if not isinstance(value, (list, tuple)):
        raise ValueError("linked_list test data must be a JSON array")
    items = list(value)
    if not items:
        return "null"

    def chain(i: int) -> str:
        if i == len(items) - 1:
            return f"new ListNode({java_literal(items[i], of)})"
        return f"new ListNode({java_literal(items[i], of)}, {chain(i + 1)})"

    return chain(0)


def cpp_listnode_literal(value, schema: dict) -> str:
    """value: JSON list -> nested `new ListNode(..., nullptr)`."""
    of = schema.get("of") or {}
    if not isinstance(value, (list, tuple)):
        raise ValueError("linked_list test data must be a JSON array")
    items = list(value)
    if not items:
        return "nullptr"

    def chain(i: int) -> str:
        if i == len(items) - 1:
            return f"new ListNode({cpp_literal(items[i], of)}, nullptr)"
        return f"new ListNode({cpp_literal(items[i], of)}, {chain(i + 1)})"

    return chain(0)


def schema_is_linked_list(schema: dict | None) -> bool:
    return isinstance(schema, dict) and schema.get("kind") == "linked_list"
