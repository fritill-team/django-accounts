# AUTHENTICATION THEMES
AUTHENTICATION_THEME_CORPORATE = 'corporate'
AUTHENTICATION_THEME_CREATIVE = 'creative'
AUTHENTICATION_THEME_OVERLAY = 'overlay'
AUTHENTICATION_THEME_FANCY = 'fancy'

AUTHENTICATION_THEME = AUTHENTICATION_THEME_CORPORATE

# Multiple Authentication
MULTIPLE_AUTHENTICATION_ACTIVE = True

# LOGIN_FORM = 'django.contrib.auth.forms.AuthenticationForm'
REGISTER_FORM = 'dj_accounts.authentication.forms.RegisterForm'

# Phone Service
PHONE_VERIFY_SERVICE = 'dj_accounts.authentication.tests.mocks.TestingVerifyService'

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