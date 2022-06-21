from django.urls import path

from accounts.views_api import UpdateEmailAPIView, UpdateProfileDataAPIView, UpdatePhoneAPIView

urlpatterns = [
    path('update/', UpdateProfileDataAPIView.as_view(), name='update_profile_api'),
    path('email/update/', UpdateEmailAPIView.as_view(), name='update_email_api'),
    path('phone/update/', UpdatePhoneAPIView.as_view(), name='update_phone_api'),
]
