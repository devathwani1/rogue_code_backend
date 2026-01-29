from rest_framework import serializers
from apps.challenges.models.questions import Question

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'
        read_only_fields = ('slug', 'created_at')

    def validate_parameters(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Parameters must be a list.")
        for param in value:
            if not isinstance(param, dict):
                raise serializers.ValidationError("Each parameter must be an object.")
            if 'name' not in param or 'type' not in param:
                raise serializers.ValidationError("Each parameter must have 'name' and 'type'.")
        return value

    def validate_test_cases(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Test cases must be a list.")
        for case in value:
            if not isinstance(case, dict):
                raise serializers.ValidationError("Each test case must be an object.")
            if 'input' not in case or 'output' not in case:
                raise serializers.ValidationError("Each test case must have 'input' and 'output'.")
            
            inputs = case.get('input')
            if not isinstance(inputs, list):
                raise serializers.ValidationError("Test case 'input' must be a list.")
            
            for input_item in inputs:
                if not isinstance(input_item, dict):
                    raise serializers.ValidationError("Each input item must be an object.")
                # We check for 'name' but allow 'nmae' if it was a typo in user request, 
                # but better to stick to 'name' as standard.
                if 'name' not in input_item:
                    raise serializers.ValidationError("Each input item must have 'name' and 'value'.")
                if 'value' not in input_item:
                    raise serializers.ValidationError("Each input item must have 'value'.")
        return value
