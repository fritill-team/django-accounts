from django.urls import path

from accounts.views import UpdateProfileInfoView, ChangeEmailView, PhoneUpdateView

urlpatterns = [
    path('update/', UpdateProfileInfoView.as_view(), name='update_profile'),
    path('email/update/', ChangeEmailView.as_view(), name='update_email'),
    path('phone/update/', PhoneUpdateView.as_view(), name='update_phone'),
]
