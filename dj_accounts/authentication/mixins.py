import sys
import traceback

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.timezone import now

from .forms import MultipleLoginForm, VerifyPhoneForm
from .verify_phone import VerifyPhone
from ..utils import get_settings_value, get_class_from_settings, account_activation_token

UserModel = get_user_model()


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


class SendEmailVerificationMixin:
    def send_email_verification(self, request, user):
        try:
            html_message = render_to_string('dj_accounts/emails/email_confirmation.html', {
                'user': user,
                'site': get_current_site(request),
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
                'protocol': 'https' if request.is_secure() else 'http'
            })
            send_mail(
                subject=get_settings_value('EMAIL_CONFIRMATION_SUBJECT', None),
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


class ViewCallbackMixin:
    def get_callback(self, key, user):
        callback = get_class_from_settings(key)
        if callback:
            callback(user)


class SendPhoneVerificationMixin:
    def send_phone_verification(self, user):
        try:
            VerifyPhone().send(user.phone)
        except Exception as e:
            parts = ["Traceback (most recent call last):\n"]
            parts.extend(traceback.format_stack(limit=25)[:-2])
            parts.extend(traceback.format_exception(*sys.exc_info())[1:])
            print("".join(parts))


class RegisterMixin(ViewCallbackMixin, SendEmailVerificationMixin, SendPhoneVerificationMixin):
    def get_form_class(self):
        return get_class_from_settings('REGISTER_FORM', 'dj_accounts.authentication.forms.UserCreationForm')


class VerifyEmailMixin:
    def verify(self, uidb64, token):
        user = None
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = UserModel.objects.get(pk=uid)

        except(TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            pass
        finally:
            success = account_activation_token.check_token(user, token)
            if user is not None and success:
                user.email_verified_at = now()
                user.save()

            return success, user



