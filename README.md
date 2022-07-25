## Installation

```cd
pip install dj-accounts
```

## Configuration

```python
INSTALLED_APPS = [
    ...,

    'dj_accounts',
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



### in your settings.py
```python
# django restFramework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],

}

```