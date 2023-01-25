from .views_api import VerifyPhoneAPIView, \
    VerifyEmailAPIView, ResendPhoneVerificationAPIView, RegisterAPIView, ResendEmailVerificationLinkAPIView, \
    UserLogoutAPIView, PasswordResetAPIView, LoginAPIView, ChangePasswordAPIView
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [

    # simple jwt
    path('login/', LoginAPIView.as_view(), name='api_login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', UserLogoutAPIView.as_view(), name='logout_api'),
    path('register/', RegisterAPIView.as_view(), name='api_register'),

    # password
    path('change_password/', ChangePasswordAPIView.as_view(), name='change_password_api'),
    path('password_reset/', PasswordResetAPIView.as_view(), name='password_reset_api'),

    # email verification
    path('verify/email/resend/', ResendEmailVerificationLinkAPIView.as_view(),
         name='api_resend_email_verification'),
    path('verify/email/<str:uidb64>/<str:token>/', VerifyEmailAPIView.as_view(), name='api_verify_email'),

    # phone verification
    path('verify/phone/', VerifyPhoneAPIView.as_view(), name='verify_phone_api'),
    path('resend_phone_activation/', ResendPhoneVerificationAPIView.as_view(), name='resend_phone_activation_api'),
]
