## installation

1. in terminal, run
```
pip install dj-accounts
```
2. in settings file add:

``` python 
    INSTALLED_APPS = (
        ...
        'dj_accounts',
        'rest_framework_simplejwt.token_blacklist',
        ...
    )
```
3. add this lines to you user model to get multiple authentication:


## usage

django accounts provides various user management features for authentication and user profile management.

* Authentication urls are provided in the `dj_accounts.urls.site_urls.urls_auth` file, in urls file add:
```python
urlpatterns = [
    path('', include('dj_accounts.urls.site_urls.urls_auth')),
]
```

* Authentication API urls are provided in `dj_accounts.urls.urls_auth_api` file, in urls file add:
```python
urlpatterns = [
   path('', include('dj_accounts.urls.api_urls.urls_auth_api')),
]
```

* Profile Management urls are provided in `dj_accounts.urls.site_urls.urls_profile` file, in urls file add:
```python
urlpatterns = [
    path('', include('dj_accounts.urls.site_urls.urls_profile')),
]
```

* Profile Management API urls are provided in `dj_accounts.urls.api_urls.urls_profile_api` file, in urls file add:
```python
urlpatterns = [
   path('', include('dj_accounts.urls.api_urls.urls_profile_api')),
]
```

### Enable Multiple Authentication:

if you want to enable multiple authentication you can add the following to your settings file:

```python
...
AUTHENTICATION_BACKENDS = (
    'dj_accounts.backends.MultipleAuthenticationBackend',
    # ...
)
...
MULTIPLE_AUTHENTICATION_ACTIVE = True
...
```

this will allow you to authenticate with username, phone and email 

in your model you should add the following line:
```python
AUTHENTICATION_FIELDS = ['username', 'email', ...]

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

username = models.CharField(
    _('username'),
    max_length=150,
    unique=True,
    help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
    validators=[username_validator],
    error_messages={
        'unique': _("A user with that username already exists."),
    },
)

```


if you want to enable phone verification you can add the following to your settings file:

```python
ENABLE_PHONE_VERIFICATION_ACTIVE = True
PHONE_VERIFY_SERVICE = 'dj_accounts.tests.mocks.TestingVerifyService'
```

you can find the implementation guide for phone verification here.

## Overrides
### Change Registration Form:

if you want to use your own registration form you can add the following to your settings file:

```python
...
REGISTER_FORM = 'path.to.the.form.RegisterForm'
...
```

### Change Profile Serializer:

if you want to use your own profile serializer to update profile data you can add the following to your settings file:

```python
...
PROFILE_SERIALIZER = 'path.to.the.form.PROFILE_SERIALIZER'
...
```

### Update Email Form:

if you want to use your own update email form you can add the following to your settings file:

```python
...
UPDATE_EMAIL_FORM = 'path.to.the.form.UPDATE_EMAIL_FORM'
...
```

### Update Phone Form:

if you want to use your own update phone form you can add the following to your settings file:

```python
...
UPDATE_PHONE_FORM = 'path.to.the.form.UPDATE_PHONE_FORM'
...
```