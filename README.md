# Django Accounts

* pypi: [Django Accounts](https://pypi.org/project/dj-accounts/1.0.0/)
* authors (github): [@MahmoudNasser](https://github.com/elMeniwy), [@SohaybeKhaled](https://github.com/Sohype-Khaled)

## Installation

```cd
pip install dj-accounts
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
    # for site authentication
    path('', include('accounts.urls_auth')),
    
    # for site profile
    path('', include('accounts.urls_profile')),
   
]
```

### in urls of API

```python
urlpatterns = [
    ....
    # for api authentication
    path('', include('accounts.urls_auth_api')),
    # for api authentication
    path('', include('accounts.urls_profile_api')),
]
```

### in your settings.py

```python

# for custom register form
REGISTER_FORM = 'users.form.RegisterForm'



# django restFramework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],

}
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

### Phone Verification Service
* Twilio

1. install twilio

2. in your `settings.py`
```python

# for using test verify service
PHONE_VERIFY_SERVICE = 'accounts.tests.mocks.TestingVerifyService'

# for custom verify phone service
# PHONE_VERIFY_SERVICE = 'path.to.TwilioVerifyPhoneService'

# Twilio Settings
TWILIO_VERIFY_SERVICE_SID = os.environ.get('TWILIO_VERIFY_SERVICE_SID')
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
```

3. create custom service for twilio
```python
from accounts.verify_phone import VerifyPhoneServiceAbstract
from django.conf import settings
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

Twilio_Client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
Twilio_Client_Verify = Twilio_Client.verify.services(settings.TWILIO_VERIFY_SERVICE_SID)


class TwilioVerifyPhoneService(VerifyPhoneServiceAbstract):
    def send(self, phone):
        Twilio_Client_Verify.verifications.create(to=phone, channel='sms')

    def check(self, phone, code):
        try:
            result = Twilio_Client_Verify.verification_checks.create(to=phone, code=code)
        except TwilioRestException:
            return False
        return result.status == 'approved'
``` 

