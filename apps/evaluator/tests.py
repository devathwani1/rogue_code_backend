from django.test import SimpleTestCase

from apps.evaluator.services.linked_list_literals import (
    cpp_listnode_literal,
    java_listnode_literal,
)
from apps.evaluator.services.source_literals import java_literal


class LinkedListLiteralTests(SimpleTestCase):
    def test_java_chain(self):
        schema = {"kind": "linked_list", "of": {"kind": "primitive", "name": "int"}}
        lit = java_listnode_literal([1, 2, 3], schema)
        self.assertIn("new ListNode(1", lit)
        self.assertIn("new ListNode(3)", lit)

    def test_java_empty(self):
        schema = {"kind": "linked_list", "of": {"kind": "primitive", "name": "int"}}
        self.assertEqual(java_listnode_literal([], schema), "null")

    def test_cpp_chain(self):
        schema = {"kind": "linked_list", "of": {"kind": "primitive", "name": "int"}}
        lit = cpp_listnode_literal([1, 2], schema)
        self.assertIn("nullptr", lit)
        self.assertIn("new ListNode(1", lit)

    def test_java_literal_dispatches_linked_list(self):
        schema = {"kind": "linked_list", "of": {"kind": "primitive", "name": "int"}}
        lit = java_literal([5], schema)
        self.assertIn("ListNode", lit)
