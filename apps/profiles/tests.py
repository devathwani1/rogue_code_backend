from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.challenges.services.day_rollover_service import DayRolloverService, _ist_date
from apps.profiles.models import Profile

User = get_user_model()


class ResetRunViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="reset@test.com",
            email="reset@test.com",
            password="secret123",
        )
        self.profile = Profile.objects.create(
            user=self.user,
            lives=0,
            joined_challenge_at=timezone.now(),
        )

    def test_reset_requires_auth(self):
        res = self.client.post("/profiles/me/reset-run/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reset_rejected_when_lives_not_zero(self):
        self.profile.lives = 3
        self.profile.save()
        self.client.force_authenticate(self.user)
        res = self.client.post("/profiles/me/reset-run/")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_ok_when_all_lives_lost(self):
        self.client.force_authenticate(self.user)
        res = self.client.post("/profiles/me/reset-run/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data.get("success"))
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.lives, 3)
        self.assertEqual(self.profile.challenge_day, 1)
        self.assertEqual(self.profile.streak, 0)
        self.assertEqual(
            self.profile.last_closed_ist_date,
            _ist_date(timezone.now()) - timedelta(days=1),
        )
        # Loading profile stats must not fire catch-up rollovers that burn a core.
        DayRolloverService.process_user(self.user)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.lives, 3)
