from rest_framework import serializers
from apps.common.models import Difficulty

class DifficultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Difficulty
        fields = ('id', 'name', 'mode_name', 'logo', 'days', 'number_of_questions')
