import random
import string

from adrf.views import APIView
from asgiref.sync import sync_to_async
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response

from .models import CustomUser, Referral, ReferralCode
from .serializers import ReferralCodeSerializer, ReferralSerializer


class ReferralCodeViewSet(APIView):

    async def post(self, request):
        referral_code = await sync_to_async(
            lambda: getattr(request.user, "referral_code", None)
        )()
        if referral_code:
            await sync_to_async(referral_code.delete)()
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
        expires_at = timezone.now() + timezone.timedelta(days=7)
        referral_code = await sync_to_async(ReferralCode.objects.create)(
            user=request.user, code=code, expires_at=expires_at
        )
        serializer = ReferralCodeSerializer(referral_code)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    async def delete(self, request):
        referral_code = await sync_to_async(
            lambda: getattr(request.user, "referral_code", None)
        )()
        if referral_code:
            await sync_to_async(referral_code.delete)()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "No active referral code found."},
            status=status.HTTP_404_NOT_FOUND,
        )


class ReferralViewSet(APIView):

    async def get(self, request, email):
        try:
            referrer = await sync_to_async(CustomUser.objects.get)(email=email)
            referral_code = await sync_to_async(
                lambda: getattr(referrer, "referral_code", None)
            )()
            if referral_code:
                serializer = ReferralCodeSerializer(referral_code)
                return Response(serializer.data)
            return Response(
                {"detail": "No active referral code for this user."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except CustomUser.DoesNotExist:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

    async def post(self, request):
        ref_code = request.data.get("referral_code")
        try:
            referrer_code = await sync_to_async(ReferralCode.objects.get)(code=ref_code)
            if await sync_to_async(referrer_code.is_expired)():
                return Response(
                    {"detail": "Referral code is expired."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            referrer = await sync_to_async(lambda: referrer_code.user)()
            referral_exists = await sync_to_async(
                Referral.objects.filter(referrer=referrer, referred=request.user).exists
            )()
            if referral_exists:
                return Response(
                    {"detail": "Referral already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            await sync_to_async(Referral.objects.create)(
                referrer=referrer, referred=request.user
            )
            return Response(
                {"detail": "User registered with referral code."},
                status=status.HTTP_201_CREATED,
            )
        except ReferralCode.DoesNotExist:
            return Response(
                {"detail": "Invalid referral code."}, status=status.HTTP_404_NOT_FOUND
            )


class ReferralListViewSet(APIView):

    async def get(self, request, referrer_id):
        try:
            referrer = await sync_to_async(CustomUser.objects.get)(id=referrer_id)
            referrals = await sync_to_async(lambda: list(referrer.referrals.all()))()
            serializer = await sync_to_async(
                lambda: ReferralSerializer(referrals, many=True).data
            )()
            return Response(serializer)
        except CustomUser.DoesNotExist:
            return Response(
                {"detail": "Referrer not found."}, status=status.HTTP_404_NOT_FOUND
            )
