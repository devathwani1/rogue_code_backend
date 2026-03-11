class JavaMapper:
    @staticmethod
    def map_primitive(name: str) -> str:
        mapping = {
            "int": "int",
            "bool": "boolean",
            "string": "String"
        }
        return mapping.get(name, "Object")

    @staticmethod
    def to_java_type(schema: dict) -> str:
        """
        Recursively maps a TypeSchema to a Java type string.
        """
        if not schema or not isinstance(schema, dict):
            return "Object"

        kind = schema.get("kind")

        if kind == "primitive":
            return JavaMapper.map_primitive(schema.get("name", ""))

        elif kind == "array":
            of_schema = schema.get("of")
            if of_schema:
                inner_type = JavaMapper.to_java_type(of_schema)
                # Convert primitive to wrapper for List
                wrapper_mapping = {"int": "Integer", "boolean": "Boolean"}
                inner_type = wrapper_mapping.get(inner_type, inner_type)
                return f"List<{inner_type}>"
            return "List"

        elif kind == "map":
            key_schema = schema.get("key")
            value_schema = schema.get("value")
            if key_schema and value_schema:
                k = JavaMapper.to_java_type(key_schema)
                v = JavaMapper.to_java_type(value_schema)
                # Convert primitive to wrapper for Map
                wrapper_mapping = {"int": "Integer", "boolean": "Boolean"}
                k = wrapper_mapping.get(k, k)
                v = wrapper_mapping.get(v, v)
                return f"Map<{k}, {v}>"
            return "Map"

        elif kind == "linked_list":
            return "ListNode"

        elif kind == "tree":
            return "TreeNode"

        elif kind == "graph":
            return "Node"

        return "Object"

    @staticmethod
    def generate_java_starter_code(function_name: str, parameters: list, return_type: dict) -> str:
        """
        Generates a Java starter code string containing the class and method signature.
        """
        params_list = []
        all_params_str = ""
        for param in parameters:
            name = param.get("name", "arg")
            schema = param.get("type_schema", {})
            type_hint = JavaMapper.to_java_type(schema)
            params_list.append(f"{type_hint} {name}")
            all_params_str += f" {type_hint} "
        
        params_str = ", ".join(params_list)
        return_hint = JavaMapper.to_java_type(return_type)
        
        # Check if helper classes are needed
        param_types = [p.split(" ")[0] for p in params_list]
        all_types = param_types + [return_hint]
        
        helper_classes = ""
        if "ListNode" in all_types:
            helper_classes += "class ListNode {\n    int val;\n    ListNode next;\n    ListNode() {}\n    ListNode(int val) { this.val = val; }\n    ListNode(int val, ListNode next) { this.val = val; this.next = next; }\n}\n\n"

        if "TreeNode" in all_types:
            helper_classes += "class TreeNode {\n    int val;\n    TreeNode left;\n    TreeNode right;\n    TreeNode() {}\n    TreeNode(int val) { this.val = val; }\n    TreeNode(int val, TreeNode left, TreeNode right) {\n        this.val = val;\n        this.left = left;\n        this.right = right;\n    }\n}\n\n"

        if "Node" in all_types:
            helper_classes += "class Node {\n    public int val;\n    public List<Node> neighbors;\n    public Node() {\n        val = 0;\n        neighbors = new ArrayList<Node>();\n    }\n    public Node(int _val) {\n        val = _val;\n        neighbors = new ArrayList<Node>();\n    }\n    public Node(int _val, ArrayList<Node> _neighbors) {\n        val = _val;\n        neighbors = _neighbors;\n    }\n}\n\n"

        all_types_str = " ".join(all_types)
        import_stmts = ""
        if "List<" in all_types_str or "Node" in all_types:
            import_stmts += "import java.util.*;\n"
        elif "Map<" in all_types_str:
            import_stmts += "import java.util.*;\n"

        starter_code = f"{import_stmts}\n{helper_classes}class Solution {{\n    public {return_hint} {function_name}({params_str}) {{\n        \n    }}\n}}"
        return starter_code
