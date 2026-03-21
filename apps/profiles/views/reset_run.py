from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.profiles.services.reset_run import ResetRunError, reset_user_run


class ResetRunView(APIView):
    """
    POST — wipe daily challenge progress and restart from day 1 (cores back to 3).
    Allowed only when the user has 0 lives (all cores destroyed).
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            reset_user_run(request.user)
        except ResetRunError as e:
            return Response({"success": False, "message": str(e)}, status=400)
        return Response(
            {
                "success": True,
                "message": "Your run has been reset. Survive again from day 1.",
            }
        )
