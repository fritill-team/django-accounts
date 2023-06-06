import importlib

from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext as _
from rest_framework_simplejwt.tokens import RefreshToken


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
                str(user.pk) + str(timestamp) + str(user.is_active)
        )


account_activation_token = TokenGenerator()


def send_mail_confirmation(request, user):
    current_site = get_current_site(request)
    mail_subject = _('Activate your account.')
    message = render_to_string('dj_accounts/confirm_email_template.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    send_mail(mail_subject, message, settings.EMAIL_HOST_USER, [user.email])


def get_user_tokens(user):
    tokens = RefreshToken.for_user(user)
    return {
        "access_token": str(tokens.access_token),
        "refresh_token": str(tokens)
    }


def get_errors(errors):
    return {name: error[0] for name, error in errors.items()}


def get_settings_value(settings_key, default_value=None):
    return getattr(settings, settings_key, default_value)


def import_class_or_function(name):
    name_split = name.split('.')
    name = name_split[-1:][0]
    module_name = name_split[:-1]
    return getattr(importlib.import_module('.'.join(module_name)), name)


def get_class_from_settings(settings_key, default_class=None):
    class_name = get_settings_value(settings_key, None)

    if not class_name:
        class_name = default_class

    return import_class_or_function(class_name) if type(class_name) is str else class_name


