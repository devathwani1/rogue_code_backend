from django.test import TestCase, RequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.accounts.models.user import User
from apps.accounts.services.auth_result import AuthState, ActionRequired
from django.core import mail

class AccountsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.email = "test@example.com"
        self.password = "testpass123"
        self.age = 18

    def test_registration_flow(self):
        # 1. Register new user
        response = self.client.post(self.register_url, {
            "email": self.email,
            "password": self.password,
            "confirm_password": self.password,
            "age": self.age
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["auth_state"], AuthState.SUCCESS)
        self.assertEqual(response.data["action_required"], ActionRequired.VERIFY_EMAIL)
        self.assertEqual(User.objects.get(email=self.email).age, self.age)
        
        # Verify email sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.email, mail.outbox[0].to)

        # 2. Register same user again (unverified)
        response = self.client.post(self.register_url, {
            "email": self.email,
            "password": self.password,
            "confirm_password": self.password,
            "age": self.age
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["auth_state"], AuthState.EMAIL_NOT_VERIFIED)
        self.assertEqual(response.data["action_required"], ActionRequired.VERIFY_EMAIL)

        # 3. Verify user
        user = User.objects.get(email=self.email)
        user.is_verified = True
        user.save()

        # 4. Register same user again (verified)
        response = self.client.post(self.register_url, {
            "email": self.email,
            "password": self.password,
            "confirm_password": self.password,
            "age": self.age
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["auth_state"], AuthState.EMAIL_ALREADY_REGISTERED)
        self.assertEqual(response.data["action_required"], ActionRequired.LOGIN)

    def test_registration_rejects_users_under_18(self):
        response = self.client.post(self.register_url, {
            "email": "underage@example.com",
            "password": self.password,
            "confirm_password": self.password,
            "age": 17
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email="underage@example.com").exists())

    def test_login_unverified(self):
        # Create unverified user
        User.objects.create_user(username=self.email, email=self.email, password=self.password, is_verified=False)
        
        response = self.client.post(self.login_url, {
            "email": self.email,
            "password": self.password
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["auth_state"], AuthState.EMAIL_NOT_VERIFIED)
        self.assertEqual(response.data["action_required"], ActionRequired.VERIFY_EMAIL)

    def test_generate_tokens_type(self):
        from apps.accounts.services.auth import AuthService
        user = User.objects.create_user(username="token@test.com", email="token@test.com", password="pass")
        token = AuthService.generate_tokens(user)
        self.assertIsInstance(token, str)
