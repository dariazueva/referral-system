from django.contrib import admin

from . import models


@admin.register(models.ReferralCode)
class ReferralCodeAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "created_at", "expires_at")


@admin.register(models.Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ("referrer", "referred", "created_at")
