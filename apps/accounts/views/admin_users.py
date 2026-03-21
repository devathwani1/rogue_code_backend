from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from apps.accounts.models import User
from apps.accounts.serializers.admin_users import AdminUserSerializer
from apps.common.utils import Utils


class AdminUserListView(APIView):
    """Staff-only: all users with profile summary for admin dashboard."""

    permission_classes = [IsAdminUser]

    def get(self, request):
        qs = (
            User.objects.all()
            .select_related("profile", "profile__difficulty")
            .order_by("-date_joined")
        )
        count = qs.count()
        serializer = AdminUserSerializer(qs, many=True)
        return Response(
            Utils.success_response_data(
                message="Users retrieved successfully",
                data={"count": count, "users": serializer.data},
            )
        )
