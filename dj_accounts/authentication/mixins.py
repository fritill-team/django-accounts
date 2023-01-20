from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext as _

from dj_accounts.authentication.forms import MultipleLoginForm
from ..utils import get_settings_value, get_class_from_settings, account_activation_token


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
        current_site = get_current_site(request)
        mail_subject = _('Activate your account.')
        message = render_to_string('dj_accounts/emails/email_confirmation.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        # try:
        # send_email_confirmation(request, user)
        # except Exception as e:
        #     parts = ["Traceback (most recent call last):\n"]
        #     parts.extend(traceback.format_stack(limit=25)[:-2])
        #     parts.extend(traceback.format_exception(*sys.exc_info())[1:])
        #     print("".join(parts))

    def call_send_phone_verification(self, user):
        pass
