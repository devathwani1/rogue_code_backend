from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.profiles.models import Profile


class LeaderboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rows = (
            Profile.objects.select_related("user", "difficulty")
            .filter(user__is_staff=False)
            .order_by("-level", "-max_streak", "-streak", "-challenge_day", "user__date_joined")
        )

        data = []
        for idx, p in enumerate(rows, start=1):
            user = p.user
            data.append(
                {
                    "rank": idx,
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                    "difficulty": getattr(p.difficulty, "name", None),
                    "level": p.level,
                    "streak": p.streak,
                    "max_streak": p.max_streak,
                    "challenge_day": p.challenge_day,
                }
            )

        return Response(data)
