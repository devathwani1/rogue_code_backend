from rest_framework import serializers
from django.db import transaction
from apps.challenges.models import Question, QuestionParameter, TestCase
from apps.challenges.models.progress import DailyPlanItemSolve
from apps.challenges.utils.solve_language import get_solve_language

class QuestionParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionParameter
        fields = ('name', 'type_schema', 'order')

class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = ('input_data', 'expected_output', 'is_hidden')

class QuestionSerializer(serializers.ModelSerializer):
    parameters = QuestionParameterSerializer(many=True)
    test_cases = TestCaseSerializer(many=True)

    class Meta:
        model = Question
        fields = (
            'id', 'title', 'slug', 'description', 'constraints', 
            'difficulty', 'function_name', 'return_type', 
            'parameters', 'test_cases', 'created_at'
        )
        read_only_fields = ('id', 'slug', 'created_at')

    def validate_type_schema(self, schema):
        if not isinstance(schema, dict):
            raise serializers.ValidationError("Type schema must be a dictionary.")
        
        kind = schema.get("kind")
        if kind not in ["primitive", "array", "map", "linked_list", "tree", "graph"]:
            raise serializers.ValidationError(
                f"Invalid kind: {kind}. Supported: primitive, array, map, linked_list, tree, graph."
            )

        if kind == "primitive":
            name = schema.get("name")
            if name not in ["int", "bool", "string"]: 
                raise serializers.ValidationError(f"Invalid primitive: {name}. Supported: int, bool, string.")
        
        elif kind == "array":
            of = schema.get("of")
            if not of:
                raise serializers.ValidationError("Array type must specify 'of'.")
            self.validate_type_schema(of)

        elif kind == "map":
            key = schema.get("key")
            value = schema.get("value")
            if not key or not value:
                raise serializers.ValidationError("Map type must specify 'key' and 'value'.")
            self.validate_type_schema(key)
            self.validate_type_schema(value)
            
            if key.get("kind") != "primitive":
                 raise serializers.ValidationError("Map keys must be primitive types.")

        elif kind == "linked_list":
            of = schema.get("of")
            if not of:
                raise serializers.ValidationError(
                    "linked_list must specify 'of' (element type schema)."
                )
            self.validate_type_schema(of)

        return schema

    def validate_return_type(self, value):
        return self.validate_type_schema(value)

    def validate(self, data):
        parameters_data = data.get('parameters', [])
        for param in parameters_data:
            self.validate_type_schema(param.get('type_schema'))
        return data

    @transaction.atomic
    def create(self, validated_data):
        parameters_data = validated_data.pop('parameters')
        test_cases_data = validated_data.pop('test_cases')
        
        question = Question.objects.create(**validated_data)
        
        for param_data in parameters_data:
            QuestionParameter.objects.create(question=question, **param_data)
            
        for case_data in test_cases_data:
            TestCase.objects.create(question=question, **case_data)
            
        return question

    @transaction.atomic
    def update(self, instance, validated_data):
        parameters_data = validated_data.pop("parameters", None)
        test_cases_data = validated_data.pop("test_cases", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if parameters_data is not None:
            instance.parameters.all().delete()
            for param_data in parameters_data:
                QuestionParameter.objects.create(question=instance, **param_data)

        if test_cases_data is not None:
            instance.test_cases.all().delete()
            for case_data in test_cases_data:
                TestCase.objects.create(question=instance, **case_data)

        return instance

class QuestionSolveSerializer(serializers.ModelSerializer):
    parameters = QuestionParameterSerializer(many=True, read_only=True)
    test_cases = serializers.SerializerMethodField()
    starter_code = serializers.SerializerMethodField()
    language = serializers.SerializerMethodField()
    solve_status = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = (
            'id', 'title', 'slug', 'description', 'constraints',
            'difficulty', 'function_name', 'return_type',
            'parameters', 'test_cases', 'starter_code', 'language',
            'solve_status',
        )

    def get_test_cases(self, obj):
        test_cases = obj.test_cases.filter(is_hidden=False)
        return TestCaseSerializer(test_cases, many=True).data

    def get_solve_status(self, obj):
        """
        Current user's progress on this question (any matching DailyPlanItem).
        pending | failed | completed — null if not authenticated.
        """
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return None

        solves = DailyPlanItemSolve.objects.filter(
            user=user,
            daily_plan_item__question_id=obj.pk,
        )
        if not solves.exists():
            return "pending"
        if solves.filter(success=True).exists():
            return "completed"
        return "failed"

    def get_language(self, obj):
        request = self.context.get("request")
        return get_solve_language(request)

    def get_starter_code(self, obj):
        from apps.compiler.services.python_mapper import PythonMapper
        from apps.compiler.services.java_mapper import JavaMapper
        from apps.compiler.services.cpp_mapper import CppMapper

        request = self.context.get('request')
        language = get_solve_language(request)

        params = [
            {"name": p.name, "type_schema": p.type_schema} 
            for p in obj.parameters.all().order_by('order')
        ]

        if language == "java":
            return JavaMapper.generate_java_starter_code(
                obj.function_name, 
                params, 
                obj.return_type
            )
        
        elif language == "cpp":
            return CppMapper.generate_cpp_starter_code(
                obj.function_name,
                params,
                obj.return_type
            )
        
        # Default to Python
        return PythonMapper.generate_python_starter_code(
            obj.function_name, 
            params, 
            obj.return_type
        )
