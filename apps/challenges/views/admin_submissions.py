from __future__ import annotations

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser

from apps.challenges.models import DailyPlanItemSolve
from apps.challenges.serializers.admin_submissions import AdminSubmissionSerializer
from apps.common.utils import Utils


class AdminSubmissionListView(APIView):
    """
    Staff-only: challenge submissions (DailyPlanItemSolve), newest first.
    GET ?limit=500 — cap rows returned (default 500, max 2000). total_count is always full DB size.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        raw = request.query_params.get("limit")
        if raw is None or str(raw).strip() == "":
            limit = 500
        else:
            try:
                limit = int(raw)
            except (TypeError, ValueError):
                return Response(
                    data=Utils.error_response_data(
                        message="Invalid query",
                        error=["Query parameter 'limit' must be a positive integer."],
                    ),
                    status=status.HTTP_400_BAD_REQUEST,
                )
        limit = max(1, min(limit, 2000))

        total_count = DailyPlanItemSolve.objects.count()
        qs = (
            DailyPlanItemSolve.objects.all()
            .select_related(
                "user",
                "daily_plan_item",
                "daily_plan_item__question",
                "daily_plan_item__daily_plan",
                "daily_plan_item__daily_plan__question_plan",
                "daily_plan_item__daily_plan__question_plan__difficulty",
            )
            .order_by("-last_submitted_at")[:limit]
        )
        serializer = AdminSubmissionSerializer(qs, many=True)
        data_list = serializer.data
        return Response(
            Utils.success_response_data(
                message="Submissions retrieved successfully",
                data={
                    "total_count": total_count,
                    "returned": len(data_list),
                    "submissions": data_list,
                },
            )
        )
