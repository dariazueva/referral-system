from adrf.views import APIView
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from asgiref.sync import sync_to_async
from .models import ReferralCode, Referral
from .serializers import ReferralCodeSerializer, ReferralSerializer
import random
import string


class ReferralCodeViewSet(APIView):

    async def post(self, request):
        if hasattr(request.user, 'referral_code'):
            await sync_to_async(request.user.referral_code.delete)()

        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        expires_at = timezone.now() + timezone.timedelta(days=7)
        referral_code = await sync_to_async(ReferralCode.objects.create)(
            user=request.user,
            code=code,
            expires_at=expires_at
        )
        serializer = ReferralCodeSerializer(referral_code)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    async def delete(self, request):
        if hasattr(request.user, 'referral_code'):
            await sync_to_async(request.user.referral_code.delete)()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'No active referral code found.'}, status=status.HTTP_404_NOT_FOUND)


class ReferralViewSet(APIView):

    async def get(self, request, email):
        try:
            referrer = await sync_to_async(User.objects.get)(email=email)
            if hasattr(referrer, 'referral_code'):
                serializer = ReferralCodeSerializer(referrer.referral_code)
                return Response(serializer.data)
            return Response({'detail': 'No active referral code for this user.'}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    async def post(self, request):
        ref_code = request.data.get('referral_code')
        try:
            referrer_code = await sync_to_async(ReferralCode.objects.get)(code=ref_code)
            if referrer_code.is_expired():
                return Response({'detail': 'Referral code is expired.'}, status=status.HTTP_400_BAD_REQUEST)
            referrer = referrer_code.user
            await sync_to_async(Referral.objects.create)(
                referrer=referrer,
                referred=request.user
            )
            return Response({'detail': 'User registered with referral code.'}, status=status.HTTP_201_CREATED)
        except ReferralCode.DoesNotExist:
            return Response({'detail': 'Invalid referral code.'}, status=status.HTTP_404_NOT_FOUND)
