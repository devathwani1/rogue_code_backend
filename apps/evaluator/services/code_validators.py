import ast

ALLOWED_IMPORTS = {"collections", "math", "heapq"}

class CodeValidator(ast.NodeVisitor):
    def __init__(self, question):
        self.question = question
        self.found_function = False
        self.return_found = False

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name.split(".")[0] not in ALLOWED_IMPORTS:
                raise ValueError(f"Import '{alias.name}' not allowed")

    def visit_ImportFrom(self, node):
        if node.module is None:
            raise ValueError("Relative imports not allowed")

        if node.module.split(".")[0] not in ALLOWED_IMPORTS:
            raise ValueError(f"Import from '{node.module}' not allowed")

    def visit_FunctionDef(self, node):
        if self.found_function:
            raise ValueError("Only one function definition is allowed")

        self.found_function = True
        if node.name != self.question.function_name:
            raise ValueError(
                f"Function name must be '{self.question.function_name}'"
            )

        params_qs = self.question.parameters
        expected_list = list(params_qs.order_by("order") if hasattr(params_qs, "order_by") else params_qs)
        actual_params = node.args.args

        if len(actual_params) != len(expected_list):
            raise ValueError(
                f"Expected {len(expected_list)} parameters, got {len(actual_params)}"
            )
        for actual, expected in zip(actual_params, expected_list):
            exp_name = expected.name if hasattr(expected, "name") else expected.get("name")
            if actual.arg != exp_name:
                raise ValueError(
                    f"Expected parameter '{exp_name}', got '{actual.arg}'"
                )

        self.generic_visit(node)
    def visit_Return(self, node):
        self.return_found = True

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in {"eval", "exec", "open", "__import__"}:
                raise ValueError(f"Call to '{node.func.id}' is not allowed")

        self.generic_visit(node)

    def validate(self, tree):
        self.visit(tree)
        if not self.found_function:
            raise ValueError(
                f"Function '{self.question.function_name}' not found"
            )

        if not self.return_found:
            raise ValueError("Function must return a value")
