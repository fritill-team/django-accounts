## installation

1. in terminal, run `pip install dj-accounts`
2. in settings file add:

``` python 
    INSTALLED_APPS = (
        ...
        'accounts',
        ...
    )
```

## usage

django accounts provides various user management features for authentication and user profile management.

### Enable Phone Authentication:

if you want to enable phone authentication you can add the following to your settings file:

```python
...
AUTHENTICATION_BACKENDS = (
    'accounts.backends.UsernameOrPhoneModelBackend',
    # ...
)
...
PHONE_AUTHENTICATION_ACTIVE = True
...
```

if you want to enable phone verification you can add the following to your settings file:

```python
ENABLE_PHONE_VERIFICATION_ACTIVE = True
PHONE_VERIFY_SERVICE = 'accounts.tests.mocks.TestingVerifyService'
```

you can find the implementation guide for phone verification here.

### Change Registration Form:

if you want to use your own registration form you can add the following to your settings file:

```python
...
REGISTER_FORM = 'path.to.the.form.RegisterForm'
...
```

if you want to automatically send otp to the user after register make sure you set
the `ENABLE_PHONE_VERIFICATION_ACTIVE` to `True` and add the following to your settings file:

```python
AUTOMATIC_SEND_OTP_ON_REGISTER_ACTIVE = True
```