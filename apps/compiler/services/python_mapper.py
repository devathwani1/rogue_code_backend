class PythonMapper:
    @staticmethod
    def map_primitive(name: str) -> str:
        mapping = {
            "int": "int",
            "bool": "bool",
            "string": "str"
        }
        return mapping.get(name, "Any")

    @staticmethod
    def to_python_type(schema: dict) -> str:
        """
        Recursively maps a TypeSchema to a Python type hint string.
        """
        if not schema or not isinstance(schema, dict):
            return "Any"

        kind = schema.get("kind")

        if kind == "primitive":
            return PythonMapper.map_primitive(schema.get("name", ""))

        elif kind == "array":
            of_schema = schema.get("of")
            if of_schema:
                return f"list[{PythonMapper.to_python_type(of_schema)}]"
            return "list"

        elif kind == "map":
            key_schema = schema.get("key")
            value_schema = schema.get("value")
            if key_schema and value_schema:
                k = PythonMapper.to_python_type(key_schema)
                v = PythonMapper.to_python_type(value_schema)
                return f"dict[{k}, {v}]"
            return "dict"

        elif kind == "linked_list":
            return "ListNode"

        elif kind == "tree":
            return "TreeNode"

        elif kind == "graph":
            return "Node"

        return "Any"

    @staticmethod
    def generate_python_starter_code(function_name: str, parameters: list, return_type: dict) -> str:
        """
        Generates a Python starter code string containing the function signature.
        """
        params_list = []
        for param in parameters:
            name = param.get("name", "arg")
            schema = param.get("type_schema", {})
            type_hint = PythonMapper.to_python_type(schema)
            params_list.append(f"{name}: {type_hint}")
        
        params_str = ", ".join(params_list)
        return_hint = PythonMapper.to_python_type(return_type)
        
        starter_code = ""
        # Check if helper classes are needed
        params_types = [p.split(":")[1].strip() if ":" in p else p for p in params_list]
        all_types = params_types + [return_hint]

        if "ListNode" in all_types:
            starter_code += "class ListNode:\n    def __init__(self, val=0, next=None):\n        self.val = val\n        self.next = next\n\n"

        if "TreeNode" in all_types:
            starter_code += "class TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\n"

        if "Node" in all_types:
            starter_code += "class Node:\n    def __init__(self, val=0, neighbors=None):\n        self.val = val\n        self.neighbors = neighbors if neighbors is not None else []\n\n"

        starter_code += f"def {function_name}({params_str}) -> {return_hint}:\n    pass"
        return starter_code
