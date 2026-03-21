from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.challenges.models import (
    DailyPlan,
    DailyPlanItem,
    DailyPlanItemSolve,
    DailyPlanSolve,
    QuestionPlan,
)
from apps.challenges.serializers.plans import DailyPlanSerializer, DailyPlanItemSerializer
from apps.challenges.services.day_rollover_service import DayRolloverService
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

        DayRolloverService.process_user(user)
        profile.refresh_from_db()

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
            
        daily_plans = list(
            DailyPlan.objects.filter(question_plan=question_plan).order_by("day_number")
        )
        solves_by_plan_id = {
            s.daily_plan_id: s
            for s in DailyPlanSolve.objects.filter(
                user=user,
                daily_plan__in=daily_plans,
            )
        }
        serializer = DailyPlanSerializer(
            daily_plans,
            many=True,
            context={
                "request": request,
                "profile": profile,
                "solves_by_plan_id": solves_by_plan_id,
            },
        )
        
        return Response(Utils.success_response_data(
            message="Daily plans retrieved successfully",
            data=serializer.data
        ))


class DailyPlanItemListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, daily_plan_id):
        try:
            items = list(
                DailyPlanItem.objects.filter(daily_plan_id=daily_plan_id)
                .select_related("question")
                .order_by("order")
            )
            item_ids = [i.pk for i in items]
            solve_map = {
                s.daily_plan_item_id: s
                for s in DailyPlanItemSolve.objects.filter(
                    user=request.user,
                    daily_plan_item_id__in=item_ids,
                )
            }
            serializer = DailyPlanItemSerializer(
                items,
                many=True,
                context={
                    "request": request,
                    "item_solve_map": solve_map,
                },
            )
            return Response(Utils.success_response_data(
                message="Daily plan items retrieved successfully",
                data=serializer.data
            ))
        except Exception as e:
            return Response(Utils.error_response_data(
                message="Failed to retrieve daily plan items",
                error=[str(e)]
            ), status=status.HTTP_400_BAD_REQUEST)
