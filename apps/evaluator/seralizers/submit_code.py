from rest_framework import serializers


class SubmitCodeSerializer(serializers.Serializer):
    question_id = serializers.UUIDField()
    code = serializers.CharField(allow_blank=True)

    def to_internal_value(self, data):
        # Accept camelCase from frontend
        if "questionId" in data and "question_id" not in data:
            data = {**data, "question_id": data["questionId"]}
        return super().to_internal_value(data)

