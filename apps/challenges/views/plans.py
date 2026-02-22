from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.challenges.models import QuestionPlan, DailyPlan, DailyPlanItem
from apps.challenges.serializers.plans import DailyPlanSerializer, DailyPlanItemSerializer
from apps.common.utils import Utils

class DailyPlanListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = getattr(user, 'profile', None)
        
        if not profile:
            return Response(Utils.error_response_data(
                message="Profile not found",
                error=["User profile does not exist."]
            ), status=status.HTTP_404_NOT_FOUND)
            
        if not profile.difficulty:
            return Response(Utils.error_response_data(
                message="Difficulty not set",
                error=["Please set your difficulty in your profile."]
            ), status=status.HTTP_400_BAD_REQUEST)
            
        # Get active plan for this difficulty
        question_plan = QuestionPlan.objects.filter(
            difficulty=profile.difficulty,
            is_active=True
        ).first()
        
        if not question_plan:
            return Response(Utils.error_response_data(
                message="No active plan found",
                error=[f"No active question plan found for difficulty: {profile.difficulty.name}"]
            ), status=status.HTTP_404_NOT_FOUND)
            
        daily_plans = DailyPlan.objects.filter(question_plan=question_plan).order_by('day_number')
        serializer = DailyPlanSerializer(daily_plans, many=True)
        
        return Response(Utils.success_response_data(
            message="Daily plans retrieved successfully",
            data=serializer.data
        ))


class DailyPlanItemListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, daily_plan_id):
        try:
            items = DailyPlanItem.objects.filter(daily_plan_id=daily_plan_id).order_by('order')
            serializer = DailyPlanItemSerializer(items, many=True)
            return Response(Utils.success_response_data(
                message="Daily plan items retrieved successfully",
                data=serializer.data
            ))
        except Exception as e:
            return Response(Utils.error_response_data(
                message="Failed to retrieve daily plan items",
                error=[str(e)]
            ), status=status.HTTP_400_BAD_REQUEST)
