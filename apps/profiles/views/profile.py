from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.challenges.services.day_rollover_service import DayRolloverService
from apps.profiles.serializers.profile import ProfileSerializer


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        DayRolloverService.process_user(request.user)
        profile = request.user.profile
        profile.refresh_from_db()
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def patch(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(
            profile,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
