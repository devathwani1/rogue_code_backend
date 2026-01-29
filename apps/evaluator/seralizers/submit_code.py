from rest_framework import serializers

class SubmitCodeSerializer(serializers.Serializer):
    question_slug = serializers.CharField()
    code = serializers.CharField()

