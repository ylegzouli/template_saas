from django.contrib import admin
from .models import UserProfile, SubscriptionPlan, UserSubscription

admin.site.register(UserProfile)
admin.site.register(SubscriptionPlan)
admin.site.register(UserSubscription)

