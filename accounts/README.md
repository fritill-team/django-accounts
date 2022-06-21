## TODO

* Views
    * [x] LoginView
    * [x] RegisterView
    * [x] ResendVerificationOTPView
    * [ ] VerifyPhoneView
    * [ ] PhoneVerificationCompleteView
    * [ ] VerifyEmailView
    * [ ] EmailVerificationCompleteView
    * [ ] ChangeEmailView
    * [ ] ChangePhoneView
    * [ ] ChangeProfileView
* APIViews
    * [ ] LoginAPIView
    * [ ] RegisterAPIView
    * [ ] ResendVerificationOTPAPIView
    * [ ] VerifyPhoneAPIView
    * [ ] ResendVerificationEmailAPIView
    * [ ] VerifyEmailAPIView
    * [ ] ChangeEmailAPIView
    * [ ] ChangePhoneAPIView
    * [ ] ChangeProfileAPIView
    * [ ] PasswordChangeAPIView
    * [ ] LogoutAPIView
    * [ ] PasswordResetAPIView
* Forms and Form Fields
    * [ ] LoginForm
    * [ ] RegisterForm
    * [ ] ResendVerificationOTPForm
    * [ ] VerifyPhoneForm
    * [ ] VerifyEmailForm
    * [ ] ChangeEmailForm
    * [ ] ChangePhoneForm
    * [ ] ChangeProfileForm
    * [ ] PasswordChangeForm
    * [ ] PasswordResetForm
* Services
* Models

## Models

In your `User` model add the following fields

```python
from django.db import models

email_verified_at = models.DateTimeField(blank=True, null=True)
```

### Registration

`RegisterView` will handle the registration process. if you want to implement your registration logic create
new `RegisterForm` and pass it to settings file

```
REGISTER_FORM = NewRegisterForm
```

### Phone Authentication

Add `phone` field and `email_verified_at` field to `User` model

```python
from django.db import models
from django.utils.translation import gettext_lazy as _

phone = models.CharField(max_length=50, blank=False, null=False, unique=True,
                         error_messages={'unique': _("A user with that phone already exists.")})
phone_verified_at = models.DateTimeField(blank=True, null=True)
```

and in `settings` file set

```python
PHONE_AUTHENTICATION_ACTIVE = True

AUTHENTICATION_BACKENDS = (
    # ...
    'apps.users.auth.backends.UsernameOrPhoneModelBackend',
    # ...     
)
```
