import importlib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.views import View

from dj_accounts.profile.forms import UpdateEmailForm, UpdatePhoneNumberForm


class UpdateProfileView(LoginRequiredMixin, View):
    def get_form_class(self):
        form_class = getattr(settings, "PROFILE_FORM", 'dj_accounts.forms.UserChangeForm')
        if type(form_class) is str:
            form_class_split = form_class.split('.')
            class_name = form_class_split[-1:][0]
            module_name = form_class_split[:-1]
            return getattr(importlib.import_module('.'.join(module_name)), class_name)
        return form_class

    def get(self, request, *args, **kwargs):
        return render(request, 'dj_accounts/update_user_data_form.html', {
            'form': self.get_form_class(),
            "page_title": _("Update User Info")
        })

    def post(self, request, *args, **kwargs):
        form = self.get_form_class()(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, _('your profile has been updated successfully'))
            return redirect(settings.LOGIN_REDIRECT_URL)
        return render(request, 'dj_accounts/update_user_data_form.html', {
            'form': form
        })


class ChangeEmailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'dj_accounts/update_email_form.html', {
            'form': UpdateEmailForm(),
            "page_title": _("Update Email")
        })

    def post(self, request, *args, **kwargs):
        user = request.user
        form = UpdateEmailForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'your email has been updated successfully')
            return redirect(settings.LOGIN_REDIRECT_URL)

        return render(request, 'dj_accounts/update_email_form.html', {
            'form': form
        })


class ChangePhoneView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'dj_accounts/update_phone_number_form.html', {
            'form': UpdatePhoneNumberForm(),
            "page_title": _("Update Phone Number")
        })

    def post(self, request, *args, **kwargs):
        user = request.user
        form = UpdatePhoneNumberForm(user, request.POST)
        if form.is_valid():
            request.user.phone_verified_at = None
            request.user.save()
            return redirect(settings.LOGIN_REDIRECT_URL)

        return render(request, 'dj_accounts/update_phone_number_form.html', {
            "form": form
        })