from django.conf import settings
from django.contrib.auth import login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.views import View

from dj_accounts.utils import get_settings_value
from .mixins import LoginGetFormClassMixin, RegisterMixin, SendEmailVerificationMixin, ViewCallbackMixin, \
    VerifyEmailMixin, SendPhoneVerificationMixin, VerifyPhoneMixin

UserModel = get_user_model()


class LoginView(LoginGetFormClassMixin, BaseLoginView):
    redirect_authenticated_user = True

    def get_template_names(self):
        """
        returns the template based on selected theme in settings
        """
        return ['dj_accounts/authentication/themes/{}/login.html'.format(
            get_settings_value('AUTHENTICATION_THEME', 'corporate'))]


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


class VerifyPhoneView(VerifyPhoneMixin, LoginRequiredMixin, SendPhoneVerificationMixin, ViewCallbackMixin, View):

    def get_template_name(self):
        return 'dj_accounts/authentication/themes/{}/verify_phone.html'.format(
            get_settings_value('AUTHENTICATION_THEME', 'corporate'))

    def get(self, request, *args, **kwargs):
        self.get_phone()

        if self.is_verified:
            return redirect(settings.LOGIN_REDIRECT_URL)

        self.send_phone_verification(self.request.user)

        self.get_form()

        return render(request, self.get_template_name(), self.get_context())

    def post(self, request, *args, **kwargs):
        self.get_phone()

        if self.is_verified:
            return redirect(settings.LOGIN_REDIRECT_URL)

        self.get_form(request.POST)

        if self.form.is_valid():
            self.get_callback("VERIFY_PHONE_CALLBACK", request.user)
            return redirect(settings.LOGIN_REDIRECT_URL)

        return render(request, self.get_template_name(), self.get_context())


class ResendPhoneVerificationView(LoginRequiredMixin, SendPhoneVerificationMixin, ViewCallbackMixin, View):

    def get(self, request, *args, **kwargs):
        self.send_phone_verification(request.user)
        self.get_callback("RESEND_PHONE_VERIFICATION_CALLBACK", request.user)
        return JsonResponse({
            "message": _("a new verification code was sent to your phone"),
            "otp_expiry": cache.get("{}-otp-cache-expiry-timestamp".format(self.request.user.id))
        })
