### Phone Verification Service
this is the phone verification service that you can use to send otp to the user using twilio.

1. install twilio

2. in your `settings.py`
```python

# for using test verify service
PHONE_VERIFY_SERVICE = 'accounts.tests.mocks.TestingVerifyService'

# for custom verify phone service
# PHONE_VERIFY_SERVICE = 'path.to.TwilioVerifyPhoneService'

# Twilio Settings
TWILIO_VERIFY_SERVICE_SID = 'ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
TWILIO_ACCOUNT_SID = 'ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
TWILIO_AUTH_TOKEN = 'your_auth_token'
```

3. create custom service for twilio
```python
from dj_accounts.verify_phone import VerifyPhoneServiceAbstract
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

