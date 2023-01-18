from dj_accounts.authentication.forms import MultipleLoginForm
from dj_accounts.utils import get_settings_value, get_class_from_settings


class LoginGetFormClassMixin:
    def get_form_class(self):
        """
        if MULTIPLE_AUTHENTICATION_ACTIVE is True
        - returns MultipleLoginForm
        else
        - returns the regular AuthenticationForm if LOGIN_FORM setting is not defined
        - returns the provided LOGIN_FORM if set
        """
        if get_settings_value('MULTIPLE_AUTHENTICATION_ACTIVE', False):
            return MultipleLoginForm
        return get_class_from_settings('LOGIN_FORM', 'django.contrib.auth.forms.AuthenticationForm')
