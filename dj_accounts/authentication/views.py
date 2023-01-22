import sys
import traceback

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _
from django.views import View

from dj_accounts.utils import account_activation_token, send_email_confirmation, get_settings_value
from .forms import VerifyPhoneForm
from .mixins import LoginGetFormClassMixin, RegisterMixin
from .verify_phone import VerifyPhone

UserModel = get_user_model()


class LoginView(LoginGetFormClassMixin, BaseLoginView):
    redirect_authenticated_user = True

    def get_template_names(self):
        """
        returns the template based on selected theme in settings
        """
        return ['dj_accounts/authentication/themes/{}/login.html'.format(
            get_settings_value('AUTHENTICATION_THEME', 'corporate'))]


class SendMail(View):
    def get(self, request):
        user = UserModel.objects.get(pk=1)
        try:
            RegisterMixin().send_email_confirmation(request, user)
        except Exception as e:
            print(e)
        return HttpResponse("<p>Sent</p>")


class RegisterView(RegisterMixin, View):

    def get_template_name(self):
        """
        returns the template based on selected theme in settings
        """
        return 'dj_accounts/authentication/themes/{}/register.html'.format(
            get_settings_value('AUTHENTICATION_THEME', 'corporate'))

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        return render(request, self.get_template_name(), {"form": self.get_form_class()()})

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)

        form = self.get_form_class()(request.POST)
        if form.is_valid():
            user = form.save()
            login(self.request, user)

            self.get_register_callback(user)

            self.send_email_confirmation(request, user)

            self.send_phone_verification(user)

            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            return redirect(settings.LOGIN_REDIRECT_URL)
        return render(self.request, self.get_template_name(), {"form": form})


class VerifyPhoneView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.phone_verified_at is not None:
            return redirect(settings.LOGIN_REDIRECT_URL)

        return render(request, 'dj_accounts/verify_phone.html', {
            "form": VerifyPhoneForm(user=request.user)
        })

    def post(self, request, *args, **kwargs):
        if request.user.phone_verified_at is not None:
            return redirect(settings.LOGIN_REDIRECT_URL)

        form = VerifyPhoneForm(request.POST, user=request.user)
        if form.is_valid():
            request.user.phone_verified_at = now()
            request.user.save()
            return redirect(reverse("phone-verification-complete"))

        return render(request, 'dj_accounts/verify_phone.html', {"form": form})


class PhoneVerificationCompleteView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "dj_accounts/phone_verification_complete.html")


class ResendPhoneConfirmationView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        try:
            VerifyPhone().send(request.user.phone)
        except Exception as e:
            parts = ["Traceback (most recent call last):\n"]
            parts.extend(traceback.format_stack(limit=25)[:-2])
            parts.extend(traceback.format_exception(*sys.exc_info())[1:])
            print("".join(parts))

        messages.success(request, _("A new confirmation code has been sent to your phone"))
        return redirect(reverse("verify-phone"))


class VerifyEmailView(LoginRequiredMixin, View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = UserModel.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.email_verified_at = now()
            user.save()

        return redirect('email-verification-complete')


class EmailVerificationCompleteView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'dj_accounts/email_verification_complete.html', {
            'verified': request.user.email_verified_at
        })


class ResendEmailConfirmationLinkView(View):
    def get(self, request, *args, **kwargs):
        try:
            send_email_confirmation(request, request.user)
        except Exception as e:
            parts = ["Traceback (most recent call last):\n"]
            parts.extend(traceback.format_stack(limit=25)[:-2])
            parts.extend(traceback.format_exception(*sys.exc_info())[1:])
            print("".join(parts))

        messages.success(request, 'email verification is sent successfully')
        return redirect(kwargs['next'])
