import sys
import traceback

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode

from .forms import MultipleLoginForm
from .verify_phone import VerifyPhone
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

    def send_email_confirmation(self, request, user):
        try:
            current_site = get_current_site(request)  # 'Activate your account.'
            mail_subject = get_settings_value('EMAIL_CONFIRMATION_SUBJECT', None)
            html_message = render_to_string('dj_accounts/emails/email_confirmation.html', {
                
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            send_mail(
                subject=mail_subject,
                html_message=html_message,
                message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email]
            )
        except Exception as e:
            parts = ["Traceback (most recent call last):\n"]
            parts.extend(traceback.format_stack(limit=25)[:-2])
            parts.extend(traceback.format_exception(*sys.exc_info())[1:])
            print("".join(parts))

    def send_phone_verification(self, user):
        try:
            VerifyPhone().send(user.phone)
        except Exception as e:
            parts = ["Traceback (most recent call last):\n"]
            parts.extend(traceback.format_stack(limit=25)[:-2])
            parts.extend(traceback.format_exception(*sys.exc_info())[1:])
            print("".join(parts))
