from django.urls import include, path

from .views import ReferralCodeViewSet, ReferralViewSet, ReferralListViewSet

urlpatterns = [
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),
    path("referral-code/", ReferralCodeViewSet.as_view(), name="create_referral_code"),
    path("referral/<str:email>/", ReferralViewSet.as_view(), name="retrieve_referral"),
    path("referral/", ReferralViewSet.as_view(), name="create_referral"),
    path('referrals/<int:referrer_id>/', ReferralListViewSet.as_view(), name='get_referrals'),  # Новый эндпоинт
]
