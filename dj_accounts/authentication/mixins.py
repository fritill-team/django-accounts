import sys
import traceback

from dj_accounts.authentication.forms import MultipleLoginForm
from dj_accounts.utils import get_settings_value, get_class_from_settings, send_email_confirmation


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


class RegisterMixin:
    def get_form_class(self):
        return get_class_from_settings('REGISTER_FORM', 'dj_accounts.authentication.forms.UserCreationForm')

    def get_register_callback(self, user, delay=False):
        callback = get_class_from_settings("REGISTER_CALLBACK")
        if callback:
            if delay:
                callback.delay(user)
            else:
                callback(user)

    def call_send_email_confirmation(self, request, user):
        try:
            send_email_confirmation(request, user)
        except Exception as e:
            parts = ["Traceback (most recent call last):\n"]
            parts.extend(traceback.format_stack(limit=25)[:-2])
            parts.extend(traceback.format_exception(*sys.exc_info())[1:])
            print("".join(parts))


    def call_send_phone_verification(self, user):
        pass