## installation

1. in terminal, run
```
pip install dj-accounts
```
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

* Authentication urls are provided in the `accounts.urls_auth` file, in urls file add:
```python
urlpatterns = [
    path('', include('accounts.urls_auth')),
]
```

* Authentication API urls are provided in `accounts.urls_auth_api` file, in urls file add:
```python
urlpatterns = [
   path('', include('accounts.urls_auth_api')),
]
```

* Profile Management urls are provided in `accounts.urls_profile` file, in urls file add:
```python
urlpatterns = [
   path('', include('accounts.urls_profile')),
]
```

* Profile Management API urls are provided in `accounts.urls_profile` file, in urls file add:
```python
urlpatterns = [
   path('', include('accounts.urls_profile_api')),
]
```

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

in your model you should add the following line:
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