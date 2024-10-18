from django.contrib.auth.models import User
from rest_framework import serializers

from .models import ReferralCode, Referral


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ReferralCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralCode
        fields = ['user', 'code', 'expires_at']


class ReferralSerializer(serializers.ModelSerializer):
    referred = UserSerializer()

    class Meta:
        model = Referral
        fields = ['referrer', 'referred', 'created_at']
