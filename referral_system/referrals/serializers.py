from rest_framework import serializers

from .models import CustomUser, Referral, ReferralCode


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email"]


class ReferralCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralCode
        fields = ["user", "code", "expires_at"]


class ReferralSerializer(serializers.ModelSerializer):
    referrer = UserSerializer()
    referred = UserSerializer()

    class Meta:
        model = Referral
        fields = ["referrer", "referred", "created_at"]
