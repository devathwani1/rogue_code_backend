from rest_framework import serializers
from django.db import transaction
from apps.challenges.models import Question, QuestionParameter, TestCase

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
        if kind not in ["primitive", "array", "map"]:
            raise serializers.ValidationError(f"Invalid kind: {kind}. Supported: primitive, array, map.")

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

class QuestionSolveSerializer(serializers.ModelSerializer):
    parameters = QuestionParameterSerializer(many=True, read_only=True)
    test_cases = serializers.SerializerMethodField()
    starter_code = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = (
            'id', 'title', 'slug', 'description', 'constraints', 
            'difficulty', 'function_name', 'return_type', 
            'parameters', 'test_cases', 'starter_code'
        )

    def get_test_cases(self, obj):
        test_cases = obj.test_cases.filter(is_hidden=False)
        return TestCaseSerializer(test_cases, many=True).data

    def get_starter_code(self, obj):
        from apps.compiler.services.question_mapper import QuestionMapper
        params = [
            {"name": p.name, "type_schema": p.type_schema} 
            for p in obj.parameters.all().order_by('order')
        ]
        return QuestionMapper.generate_python_starter_code(
            obj.function_name, 
            params, 
            obj.return_type
        )
