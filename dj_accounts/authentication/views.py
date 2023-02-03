from django.conf import settings
from django.contrib.auth import login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView
from django.core.cache import cache
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.views import View

from dj_accounts.utils import get_settings_value
from .forms import VerifyPhoneForm
from .mixins import LoginGetFormClassMixin, RegisterMixin, SendEmailVerificationMixin, ViewCallbackMixin, \
    VerifyEmailMixin, SendPhoneVerificationMixin

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


class VerifyPhoneView(LoginRequiredMixin, SendPhoneVerificationMixin, ViewCallbackMixin, View):
    form_class = VerifyPhoneForm

    def __init__(self, *args, **kwargs):
        super(VerifyPhoneView, self).__init__(*args, **kwargs)
        self.phone = None
        self.hashed_phone = None
        self.form = None
        self.is_verified = False

    def get_template_name(self):
        return 'dj_accounts/authentication/themes/{}/verify_phone.html'.format(
            get_settings_value('AUTHENTICATION_THEME', 'corporate'))

    def get_phone(self):
        phone_model = get_settings_value("USER_PHONE_MODEL")
        if phone_model and self.kwargs.get("phone_id", None):
            phone_object = phone_model.objects.filter(user=self.request.user, id=self.kwargs.get('phone_id'))
            if not phone_object.exists():
                raise Http404("Phone does not exists")
            self.phone = str(phone_object.phone)
            self.is_verified = phone_object.phone_verified_at is not None
        else:
            self.phone = str(self.request.user.phone)
            self.is_verified = self.request.user.phone_verified_at is not None

        self.hashed_phone = ''.join(['*' for i in self.phone[4:-3]]).join([self.phone[:4], self.phone[-3:]])

    def get_context(self):
        otp_length = get_settings_value('PHONE_VERIFICATION_CODE_LENGTH', 6)
        return {
            "hashed_phone": self.hashed_phone,
            "otp_length": otp_length,
            "otp_range": range(otp_length),
            "form": self.form,
            "otp_expiry": cache.get("{}-otp-cache-expiry-timestamp".format(self.request.user.id))
        }

    def get_form(self, *args, **kwargs):
        self.form = self.form_class(user=self.request.user, *args, **kwargs)

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
