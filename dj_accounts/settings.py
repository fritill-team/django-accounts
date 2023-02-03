# AUTHENTICATION THEMES
from django.utils.translation import gettext_lazy as _

AUTHENTICATION_THEME_CORPORATE = 'corporate'
AUTHENTICATION_THEME_CREATIVE = 'creative'
AUTHENTICATION_THEME_OVERLAY = 'overlay'
AUTHENTICATION_THEME_FANCY = 'fancy'

AUTHENTICATION_THEME = AUTHENTICATION_THEME_CORPORATE

# Multiple Authentication
MULTIPLE_AUTHENTICATION_ACTIVE = True
# OTP_VERIFICATION_TYPE  = 'HOTP'
# LOGIN_FORM = 'django.contrib.auth.forms.AuthenticationForm'
REGISTER_FORM = 'dj_accounts.authentication.forms.RegisterForm'
EMAIL_CONFIRMATION_SUBJECT = _("Activate Your Account")
# Phone Service
PHONE_VERIFY_SERVICE = 'dj_accounts.authentication.tests.mocks.MockVerifyService'

# Social Authentication
SOCIAL_AUTHENTICATION_PROVIDER_FACEBOOK = 'facebook'
SOCIAL_AUTHENTICATION_PROVIDER_GOOGLE = 'google'
SOCIAL_AUTHENTICATION_PROVIDER_TWITTER = 'twitter'

DEFAULT_SOCIAL_AUTHENTICATION_PROVIDER = SOCIAL_AUTHENTICATION_PROVIDER_FACEBOOK

SOCIAL_AUTHENTICATION_PROVIDERS = (
    (SOCIAL_AUTHENTICATION_PROVIDER_FACEBOOK, "Facebook"),
    (SOCIAL_AUTHENTICATION_PROVIDER_GOOGLE, "Goggle"),
    (SOCIAL_AUTHENTICATION_PROVIDER_TWITTER, "Twitter"),
)
