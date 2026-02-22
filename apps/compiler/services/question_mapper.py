class QuestionMapper:
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
            return QuestionMapper.map_primitive(schema.get("name", ""))

        elif kind == "array":
            of_schema = schema.get("of")
            if of_schema:
                return f"list[{QuestionMapper.to_python_type(of_schema)}]"
            return "list"

        elif kind == "map":
            key_schema = schema.get("key")
            value_schema = schema.get("value")
            if key_schema and value_schema:
                k = QuestionMapper.to_python_type(key_schema)
                v = QuestionMapper.to_python_type(value_schema)
                return f"dict[{k}, {v}]"
            return "dict"

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
            type_hint = QuestionMapper.to_python_type(schema)
            params_list.append(f"{name}: {type_hint}")
        
        params_str = ", ".join(params_list)
        return_hint = QuestionMapper.to_python_type(return_type)
        
        return f"def {function_name}({params_str}) -> {return_hint}:\n    pass"
