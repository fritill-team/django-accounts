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
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django.views import View

from dj_accounts.utils import get_settings_value
from .forms import VerifyPhoneForm
from .mixins import LoginGetFormClassMixin, RegisterMixin, SendEmailVerificationMixin, ViewCallbackMixin, \
    VerifyEmailMixin
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
            RegisterMixin().send_email_verification(request, user)
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

            self.get_callback('REGISTER_CALLBACK', user)

            self.send_email_verification(request, user)

            self.send_phone_verification(user)

            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            return redirect(settings.LOGIN_REDIRECT_URL)
        return render(self.request, self.get_template_name(), {"form": form})


class ResendEmailVerificationLinkView(SendEmailVerificationMixin, ViewCallbackMixin, LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        self.send_email_verification(request, request.user)

        self.get_callback('REGISTER_CALLBACK', request.user)

        return redirect(request.GET.get('next', settings.LOGIN_REDIRECT_URL))


class VerifyEmailView(VerifyEmailMixin, ViewCallbackMixin, View):
    def get(self, request, uidb64, token):
        success, user = self.verify(uidb64, token)
        self.get_callback("VERIFY_EMAIL_CALLBACK", user)
        return redirect('email-verification-complete')


class EmailVerificationCompleteView(LoginRequiredMixin, View):
    def get_template_name(self):
        return 'dj_accounts/authentication/themes/{}/email_verification_complete.html'.format(
            get_settings_value('AUTHENTICATION_THEME', 'corporate'))

    def get(self, request):
        return render(request, self.get_template_name(), {
            'verified': request.user.email_verified_at
        })


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


class ResendPhoneVerificationView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        try:
            VerifyPhone().send(request.user.phone)
        except Exception as e:
            parts = ["Traceback (most recent call last):\n"]
            parts.extend(traceback.format_stack(limit=25)[:-2])
            parts.extend(traceback.format_exception(*sys.exc_info())[1:])
            print("".join(parts))

        messages.success(request, _("A new verification code has been sent to your phone"))
        return redirect(reverse("verify-phone"))
