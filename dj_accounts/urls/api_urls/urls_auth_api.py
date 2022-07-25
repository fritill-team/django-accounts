from ...views_api import VerifyPhoneAPIView, \
    VerifyEmailAPIView, ResendPhoneConfirmationAPIView, UserSignupAPIView, ResendEmailConfirmationLinkAPIView, \
    UserLogoutAPIView, PasswordResetAPIView, LoginAPIView, ChangePasswordAPIView
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [

    # simple jwt
    path('login/', LoginAPIView.as_view(), name='login_api'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', UserLogoutAPIView.as_view(), name='logout_api'),
    path('signup/', UserSignupAPIView.as_view(), name='signup_api'),

    # password
    path('change_password/', ChangePasswordAPIView.as_view(), name='change_password_api'),
    path('password_reset/', PasswordResetAPIView.as_view(), name='password_reset_api'),

    # email verification
    path('verify/email/<str:uidb64>/<str:token>/', VerifyEmailAPIView.as_view(), name='verify_email_api'),
    path('resend_email_activation/', ResendEmailConfirmationLinkAPIView.as_view(), name='resend_email_activation_api'),

    # phone verification
    path('verify/phone/', VerifyPhoneAPIView.as_view(), name='verify_phone_api'),
    path('resend_phone_activation/', ResendPhoneConfirmationAPIView.as_view(), name='resend_phone_activation_api'),
]
