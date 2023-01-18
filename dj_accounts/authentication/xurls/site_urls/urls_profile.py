from ...views import UpdateProfileView, ChangeEmailView, ChangePhoneView
from django.urls import path

urlpatterns = [
    path('update-profile/', UpdateProfileView.as_view(), name='update-profile'),
    path('change-email/', ChangeEmailView.as_view(), name='change-email'),
    path('change-phone/', ChangePhoneView.as_view(), name='change-phone'),
]
