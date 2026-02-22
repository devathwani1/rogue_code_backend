from rest_framework import serializers
from apps.challenges.models import DailyPlan, DailyPlanItem

class DailyPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyPlan
        fields = ('id', 'day_number')


class DailyPlanItemSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='question.id')
    title = serializers.CharField(source='question.title')
    difficulty = serializers.CharField(source='question.difficulty')

    class Meta:
        model = DailyPlanItem
        fields = ('id', 'title', 'difficulty', 'order')
