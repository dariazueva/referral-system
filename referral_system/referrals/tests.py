from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from .models import CustomUser, Referral, ReferralCode


class ReferralCodeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@example.com", password="password123"
        )
        self.client.force_authenticate(user=self.user)

    def test_create_referral_code(self):
        response = self.client.post(reverse("create_referral_code"))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("code", response.data)
        self.assertEqual(ReferralCode.objects.count(), 1)

    def test_create_referral_code_existing_code(self):
        ReferralCode.objects.create(
            user=self.user,
            code="EXISTINGCODE",
            expires_at=timezone.now() + timezone.timedelta(days=7),
        )
        response = self.client.post(reverse("create_referral_code"))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data["code"], "EXISTINGCODE")
        self.assertEqual(ReferralCode.objects.count(), 1)

    def test_delete_referral_code(self):
        ReferralCode.objects.create(
            user=self.user,
            code="EXISTINGCODE",
            expires_at=timezone.now() + timezone.timedelta(days=7),
        )
        response = self.client.delete(reverse("create_referral_code"))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ReferralCode.objects.count(), 0)

    def test_delete_non_existent_referral_code(self):
        response = self.client.delete(reverse("create_referral_code"))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No active referral code found.")


class ReferralTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@example.com", password="password123"
        )
        self.client.force_authenticate(user=self.user)
        self.referrer = CustomUser.objects.create_user(
            username="referreruser",
            email="referrer@example.com",
            password="password123",
        )
        self.referral_code = ReferralCode.objects.create(
            user=self.referrer,
            code="REFERRALCODE",
            expires_at=timezone.now() + timezone.timedelta(days=7),
        )

    def test_get_referral_code_valid_user(self):
        response = self.client.get(
            reverse("retrieve_referral", args=[self.referrer.email])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], "REFERRALCODE")

    def test_get_referral_code_no_code(self):
        self.referral_code.delete()
        response = self.client.get(
            reverse("retrieve_referral", args=[self.referrer.email])
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["detail"], "No active referral code for this user."
        )

    def test_get_referral_code_invalid_user(self):
        response = self.client.get(
            reverse("retrieve_referral", args=["invalid@example.com"])
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "User not found.")

    def test_register_with_valid_referral_code(self):
        response = self.client.post(
            reverse("create_referral"), {"referral_code": "REFERRALCODE"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["detail"], "User registered with referral code.")
        self.assertEqual(Referral.objects.count(), 1)

    def test_register_with_expired_referral_code(self):
        self.referral_code.expires_at = timezone.now() - timezone.timedelta(days=1)
        self.referral_code.save()
        response = self.client.post(
            reverse("create_referral"), {"referral_code": "REFERRALCODE"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Referral code is expired.")
        self.assertEqual(Referral.objects.count(), 0)

    def test_register_with_invalid_referral_code(self):
        response = self.client.post(
            reverse("create_referral"), {"referral_code": "INVALIDCODE"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Invalid referral code.")
        self.assertEqual(Referral.objects.count(), 0)
