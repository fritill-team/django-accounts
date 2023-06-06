import importlib
import sys
import traceback

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm, PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .forms import UpdateEmailForm, UpdatePhoneNumberForm, MultipleLoginForm
from .forms import VerifyPhoneForm
from .utils import account_activation_token, send_mail_confirmation, get_user_tokens, get_errors, get_settings_value, \
    get_class_from_settings
from .verify_phone import VerifyPhone

UserModel = get_user_model()


class RegisterAPIView(APIView):
    access_token = None
    refresh_token = None
    token = None
    user = None
    authentication_classes = []
    permission_classes = []

    def get_form_class(self):
        form_class = getattr(settings, "REGISTER_FORM", 'dj_accounts.forms.UserCreationForm')
        if type(form_class) is str:
            form_class_split = form_class.split('.')
            class_name = form_class_split[-1:][0]
            module_name = form_class_split[:-1]
            return getattr(importlib.import_module('.'.join(module_name)), class_name)
        else:
            return form_class

    def post(self, request, *args, **kwargs):
        form = self.get_form_class()(data=request.data)
        if form.is_valid():
            self.user = form.save()

            try:
                send_mail_confirmation(request, self.user)
            except Exception as e:
                parts = ["Traceback (most recent call last):\n"]
                parts.extend(traceback.format_stack(limit=25)[:-2])
                parts.extend(traceback.format_exception(*sys.exc_info())[1:])
                print("".join(parts))

            try:
                VerifyPhone().send(self.user.phone)
            except Exception as e:
                parts = ["Traceback (most recent call last):\n"]
                parts.extend(traceback.format_stack(limit=25)[:-2])
                parts.extend(traceback.format_exception(*sys.exc_info())[1:])
                print("".join(parts))

            refresh = RefreshToken.for_user(self.user)
            return Response({
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh)
            }, status=status.HTTP_201_CREATED)
        errors = {name: error[0] for name, error in form.errors.as_data().items()}
        return Response(errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class LoginAPIView(APIView):
    authentication_classes = []
    permission_classes = []

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

    def post(self, request, *args, **kwargs):
        form = self.get_form_class()(data=request.data)
        if form.is_valid():
            user = form.user_cache
            tokens = get_user_tokens(user)
            return Response(tokens, status=status.HTTP_200_OK)

        return Response(get_errors(form.errors.as_data()), status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class UserLogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        token = request.POST.get('refresh', None)
        if not token:
            return Response({_("token field is required")}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        try:
            RefreshToken(token).blacklist()
        except TokenError:
            raise ValidationError({"refresh": _('Invalid token.')})

        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetAPIView(APIView):
    permission_classes = []
    authentication_classes = []
    email_template_name = 'dj_accounts/password_reset_email.html'
    extra_email_context = None
    from_email = None
    html_email_template_name = None
    subject_template_name = 'dj_accounts/password_reset_subject.txt'
    token_generator = default_token_generator

    def post(self, request, *args, **kwargs):
        form = PasswordResetForm(data=request.data)
        if form.is_valid():
            opts = {
                'use_https': self.request.is_secure(),
                'token_generator': self.token_generator,
                'from_email': self.from_email,
                'email_template_name': self.email_template_name,
                'subject_template_name': self.subject_template_name,
                'request': self.request,
                'html_email_template_name': self.html_email_template_name,
                'extra_email_context': self.extra_email_context,
            }
            form.save(**opts)
            return Response({"message": "{} {}".format(
                _('We’ve emailed you instructions for setting your password, '
                  'if an account exists with the email you entered. You should receive them shortly.'),
                _('If you don’t receive an email, please make sure you’ve entered '
                  'the address you registered with, and check your spam folder.'))},
                status=status.HTTP_200_OK)
        return Response(get_errors(form.errors.as_data()), status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class VerifyPhoneAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        if request.user.phone_verified_at is not None:
            return Response({'message': 'this account was activated before'}, status=status.HTTP_400_BAD_REQUEST)

        form = VerifyPhoneForm(request.POST, user=request.user)
        if form.is_valid():
            request.user.phone_verified_at = now()
            request.user.save()
            return Response(status=status.HTTP_200_OK)
        return Response(form.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class ResendPhoneConfirmationAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            VerifyPhone().send(request.user.phone)
        except Exception as e:
            parts = ["Traceback (most recent call last):\n"]
            parts.extend(traceback.format_stack(limit=25)[:-2])
            parts.extend(traceback.format_exception(*sys.exc_info())[1:])
            print("".join(parts))

        return Response({"message": _('Code was resent successfully.')}, status=status.HTTP_200_OK)


# email verification
class ResendEmailConfirmationLinkAPIView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            send_mail_confirmation(request, request.user)
        except Exception as e:
            parts = ["Traceback (most recent call last):\n"]
            parts.extend(traceback.format_stack(limit=25)[:-2])
            parts.extend(traceback.format_exception(*sys.exc_info())[1:])
            print("".join(parts))

        return Response({"message": _('Email activation link resent successfully')})


class VerifyEmailAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = UserModel.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.email_verified_at = now()
            user.save()
        return Response({"message": _('Email was verified successfully.')}, status=status.HTTP_200_OK)


class ProfileDetailsAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_profile_serializer(self):
        profile_handler = getattr(settings, "PROFILE_SERIALIZER_HANDLER",
                                  'dj_accounts.tests.profile_handlers.profile_serializer_handler')
        profile_handler_split = profile_handler.split('.')
        class_name = profile_handler_split[-1:][0]
        module_name = profile_handler_split[:-1]
        return getattr(importlib.import_module('.'.join(module_name)), class_name)()

    def get(self, request, *args, **kwargs):
        return Response(self.get_profile_serializer()(self.request.user).data, status=status.HTTP_200_OK)


class UpdateProfileAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_form_class(self):
        form_class = getattr(settings, "PROFILE_FORM", 'dj_accounts.forms.UserChangeForm')
        if type(form_class) is str:
            form_class_split = form_class.split('.')
            class_name = form_class_split[-1:][0]
            module_name = form_class_split[:-1]
            return getattr(importlib.import_module('.'.join(module_name)), class_name)
        return form_class

    def get_profile_serializer(self):
        profile_handler = getattr(settings, "PROFILE_SERIALIZER_HANDLER",
                                  'dj_accounts.tests.profile_handlers.profile_serializer_handler')
        profile_handler_split = profile_handler.split('.')
        class_name = profile_handler_split[-1:][0]
        module_name = profile_handler_split[:-1]
        return getattr(importlib.import_module('.'.join(module_name)), class_name)()

    def post(self, request, *args, **kwargs):
        form = self.get_form_class()(data=request.data, instance=request.user)
        if form.is_valid():
            form.save()
            self.request.user.refresh_from_db()
            return Response(self.get_profile_serializer()(self.request.user).data, status=status.HTTP_200_OK)
        return Response(form.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        form = PasswordChangeForm(data=request.data, user=request.user)
        if form.is_valid():
            form.save()
            return Response(data={'message': _("Password updated successfully")}, status=status.HTTP_200_OK)
        return Response(get_errors(form.errors.as_data()), status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class ChangeEmailAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        form = UpdateEmailForm(data=request.data, user=request.user)
        if form.is_valid():
            form.save()
            return Response({'message': _('Email Changed Successfully')}, status=status.HTTP_200_OK)
        return Response(get_errors(form.errors.as_data()), status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class ChangePhoneAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        form = UpdatePhoneNumberForm(data=request.data, user=request.user)
        if form.is_valid():
            form.save()
            return Response({'message': _('Phone Changed Successfully')}, status=status.HTTP_200_OK)
        return Response(get_errors(form.errors.as_data()), status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class DeleteProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        UserLogoutAPIView().post(request, *args, **kwargs)
        request.user.delete()
        return Response({
            "message": _("Account Deleted Successfully!")
        })
