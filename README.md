# Django Accounts

* pypi: [Django Accounts](https://pypi.org/project/django-accounts/)
* authors (github): [@MahmoudNasser](https://github.com/elMeniwy), [@SohaybeKhaled](https://github.com/Sohype-Khaled)

## Installation
```cd
pip install df-accounts
```

## Configuration

```python
INSTALLED_APPS = [
    ...,
    
    'accounts',
]
```


### in urls of site
```python
urlpatterns = [
    ....
    path('accounts/', include('accounts.urls')),
]
```


### in urls of API
```python
urlpatterns = [
    ....
    path('accounts/', include('accounts.urls_api_v1', namespace='accounts')),
]
```


### in your settings.py
```python
AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

PHONE_VERIFY_SERVICE = 'accounts.tests.mocks.TestingVerifyService'



# django restFramework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],

}

REST_SESSION_LOGIN = True
REST_USE_JWT = True
JWT_AUTH_COOKIE = 'jwt_access_token'
JWT_AUTH_REFRESH_COOKIE = 'jwt_refresh_token'
OLD_PASSWORD_FIELD_ENABLED = True


# default JWT settings
ACCESS_TOKEN_LIFETIME = timedelta(minutes=30)
REFRESH_TOKEN_LIFETIME = timedelta(days=1)
ROTATE_REFRESH_TOKENS = False
BLACKLIST_AFTER_ROTATION = True
VERIFYING_KEY = None
AUDIENCE = None
ISSUER = None
AUTH_HEADER_TYPES = ('Bearer',)
AUTH_TOKEN_CLASSES = ('rest_framework_simplejwt.tokens.AccessToken',)
TOKEN_TYPE_CLAIM = 'token_type'
JTI_CLAIM = 'jti',
SLIDING_TOKEN_REFRESH_EXP_CLAIM = 'refresh_exp'
SLIDING_TOKEN_LIFETIME = timedelta(minutes=5)
SLIDING_TOKEN_REFRESH_LIFETIME = timedelta(days=1)

```


### In your User model

add the following fields

```python

    email = models.EmailField(_('email address'),
                              validators=[email_validator],
                              unique=True, blank=False, null=False)
    email_verified_at = models.DateField(blank=True, null=True)
    
    phone = models.CharField(
        max_length=50,
        blank=False,
        null=False,
        unique=True,
        error_messages={'unique': _("A user with that phone already exists.")})

    phone_verified_at = models.DateTimeField(blank=True, null=True)

```
