from ...views_api import ChangeEmailAPIView, UpdateProfileAPIView, ChangePhoneAPIView
from django.urls import path

urlpatterns = [
    path('update-profile/', UpdateProfileAPIView.as_view(), name='update-profile-api'),
    path('change-email/', ChangeEmailAPIView.as_view(), name='change-email-api'),
    path('change-phone/', ChangePhoneAPIView.as_view(), name='change-phone-api'),
]
