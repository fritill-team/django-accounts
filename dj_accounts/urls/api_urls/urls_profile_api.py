from django.urls import path

from ...views_api import ChangeEmailAPIView, UpdateProfileAPIView, ChangePhoneAPIView, ChangePasswordAPIView, \
    ProfileDetailsAPIView, DeleteProfileAPIView

urlpatterns = [
    path('', ProfileDetailsAPIView.as_view(), name="user-profile"),
    path('update/password/', ChangePasswordAPIView.as_view(), name='change_password_api'),
    path('update/profile/', UpdateProfileAPIView.as_view(), name='update-profile-api'),
    path('update/email/', ChangeEmailAPIView.as_view(), name='change-email-api'),
    path('update/phone/', ChangePhoneAPIView.as_view(), name='change-phone-api'),
    path('delete/', DeleteProfileAPIView.as_view(), name='delete-profile-api'),
]
