from django.urls import path

from accounts.views_api import UpdateEmailAPIView, UpdateProfileDataAPIView, UpdatePhoneAPIView
from accounts.views import UpdateProfileInfoView, ChangeEmailView, PhoneUpdateView

urlpatterns = [

    # profile Site Urls
    path('update/', UpdateProfileInfoView.as_view(), name='update_profile'),
    path('email/update/', ChangeEmailView.as_view(), name='update_email'),
    path('phone/update/', PhoneUpdateView.as_view(), name='update_phone'),

    # profile API Urls
    path('api/v1/update/', UpdateProfileDataAPIView.as_view(), name='update_profile_api'),
    path('api/v1/email/update/', UpdateEmailAPIView.as_view(), name='update_email_api'),
    path('api/v1/phone/update/', UpdatePhoneAPIView.as_view(), name='update_phone_api'),
]
