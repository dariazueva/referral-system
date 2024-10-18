from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.utils import timezone
from .models import CustomUser, ReferralCode, Referral
from .serializers import ReferralCodeSerializer, ReferralSerializer
import random
import string
from asgiref.sync import async_to_sync


class ReferralCodeViewSet(viewsets.ViewSet):

    async def create(self, request):
        if hasattr(request.user, 'referral_code'):
            await async_to_sync(request.user.referral_code.delete)()
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        expires_at = timezone.now() + timezone.timedelta(days=7)
        referral_code = async_to_sync(ReferralCode.objects.create)(
            user=request.user,
            code=code,
            expires_at=expires_at
        )
        serializer = ReferralCodeSerializer(referral_code)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    async def delete(self, request):
        if hasattr(request.user, 'referral_code'):
            await async_to_sync(request.user.referral_code.delete)()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'No active referral code found.'}, status=status.HTTP_404_NOT_FOUND)


class ReferralViewSet(viewsets.ViewSet):

    async def retrieve(self, request, email):
        try:
            referrer = await async_to_sync(CustomUser.objects.get)(email=email)
            if hasattr(referrer, 'referral_code'):
                serializer = ReferralCodeSerializer(referrer.referral_code)
                return Response(serializer.data)
            return Response({'detail': 'No active referral code for this user.'}, status=status.HTTP_404_NOT_FOUND)
        except CustomUser.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    async def create(self, request):
        ref_code = request.data.get('referral_code')
        try:
            referrer_code = await async_to_sync(ReferralCode.objects.get)(code=ref_code)
            if referrer_code.is_expired():
                return Response({'detail': 'Referral code is expired.'}, status=status.HTTP_400_BAD_REQUEST)
            referrer = referrer_code.user
            referral = await async_to_sync(Referral.objects.create)(
                referrer=referrer,
                referred=request.user
            )
            return Response({'detail': 'User registered with referral code.'}, status=status.HTTP_201_CREATED)
        except ReferralCode.DoesNotExist:
            return Response({'detail': 'Invalid referral code.'}, status=status.HTTP_404_NOT_FOUND)
