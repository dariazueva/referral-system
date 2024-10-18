from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import ReferralCodeViewSet, ReferralViewSet

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('referral-code/', ReferralCodeViewSet.as_view(), name='create_referral_code'),
    path('referral/<str:email>/', ReferralViewSet.as_view(), name='retrieve_referral'),
    path('referral/', ReferralViewSet.as_view(), name='create_referral'),
]
