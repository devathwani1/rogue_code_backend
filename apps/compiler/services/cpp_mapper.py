class CppMapper:
    @staticmethod
    def map_primitive(name: str) -> str:
        mapping = {
            "int": "int",
            "bool": "bool",
            "string": "string"
        }
        return mapping.get(name, "auto")

    @staticmethod
    def to_cpp_type(schema: dict) -> str:
        """
        Recursively maps a TypeSchema to a C++ type string.
        """
        if not schema or not isinstance(schema, dict):
            return "auto"

        kind = schema.get("kind")

        if kind == "primitive":
            return CppMapper.map_primitive(schema.get("name", ""))

        elif kind == "array":
            of_schema = schema.get("of")
            if of_schema:
                return f"vector<{CppMapper.to_cpp_type(of_schema)}>"
            return "vector<auto>"

        elif kind == "map":
            key_schema = schema.get("key")
            value_schema = schema.get("value")
            if key_schema and value_schema:
                k = CppMapper.to_cpp_type(key_schema)
                v = CppMapper.to_cpp_type(value_schema)
                return f"unordered_map<{k}, {v}>"
            return "unordered_map<auto, auto>"

        elif kind == "linked_list":
            return "ListNode*"

        elif kind == "tree":
            return "TreeNode*"

        elif kind == "graph":
            return "Node*"

        return "auto"

    @staticmethod
    def generate_cpp_starter_code(function_name: str, parameters: list, return_type: dict) -> str:
        """
        Generates a C++ starter code string containing the class and method signature.
        """
        params_list = []
        all_types_str = ""
        for param in parameters:
            name = param.get("name", "arg")
            schema = param.get("type_schema", {})
            type_hint = CppMapper.to_cpp_type(schema)
            params_list.append(f"{type_hint} {name}")
            all_types_str += f" {type_hint} "
        
        params_str = ", ".join(params_list)
        return_hint = CppMapper.to_cpp_type(return_type)
        all_types_str += f" {return_hint} "

        includes = "#include <iostream>\n#include <vector>\n#include <string>\n#include <unordered_map>\n#include <algorithm>\n\nusing namespace std;\n\n"
        
        helper_classes = ""
        # Check if ListNode is needed
        if "ListNode*" in all_types_str:
            helper_classes += "/**\n * Definition for singly-linked list.\n * struct ListNode {\n *     int val;\n *     ListNode *next;\n *     ListNode() : val(0), next(nullptr) {}\n *     ListNode(int x) : val(x), next(nullptr) {}\n *     ListNode(int x, ListNode *next) : val(x), next(next) {}\n * };\n */\n\n"

        # Check if TreeNode is needed
        if "TreeNode*" in all_types_str:
            helper_classes += "/**\n * Definition for a binary tree node.\n * struct TreeNode {\n *     int val;\n *     TreeNode *left;\n *     TreeNode *right;\n *     TreeNode() : val(0), left(nullptr), right(nullptr) {}\n *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}\n *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}\n * };\n */\n\n"

        # Check if Node is needed (Graph)
        if "Node*" in all_types_str:
            helper_classes += "/*\n// Definition for a Node.\nclass Node {\npublic:\n    int val;\n    vector<Node*> neighbors;\n    Node() {\n        val = 0;\n        neighbors = vector<Node*>();\n    }\n    Node(int _val) {\n        val = _val;\n        neighbors = vector<Node*>();\n    }\n    Node(int _val, vector<Node*> _neighbors) {\n        val = _val;\n        neighbors = _neighbors;\n    }\n};\n*/\n\n"

        starter_code = f"{includes}{helper_classes}class Solution {{\npublic:\n    {return_hint} {function_name}({params_str}) {{\n        \n    }}\n}};"
        return starter_code
