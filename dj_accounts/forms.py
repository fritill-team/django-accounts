from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .verify_phone import VerifyPhone

UserModel = get_user_model()


class UserCreationForm(BaseUserCreationForm):
    class Meta(BaseUserCreationForm.Meta):
        model = UserModel


class RegisterForm(UserCreationForm):
    username = forms.CharField(
        required=True,
        max_length=100, help_text=_("Required, please provide your username"))

    email = forms.EmailField(
        required=True,
        max_length=100, help_text=_("Required, please provide your email"))

    phone = forms.CharField(
        required=True,
        max_length=100, help_text=_("Required, please provide your phone number"))

    class Meta:
        model = UserModel
        fields = ("username", 'email', 'phone', 'password1', 'password2')

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if UserModel.objects.filter(phone=phone).exists():
            raise ValidationError("Phone already exists", code="unique")
        return phone

    def clean_email(self):
        email = self.cleaned_data['email']
        if UserModel.objects.filter(email=email).exists():
            raise ValidationError("Email already exists", code="unique")
        return email


class MultipleLoginForm(forms.ModelForm):
    password = forms.CharField(
        label=_("Password"),
        required=True,
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )
    remember_me = forms.BooleanField(
        required=False,
        label=_('Remember Me'),
        initial=False
    )

    error_messages = {
        'invalid_login': _(
            "Please enter a correct credentials. Note that "
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
        "invalid_credentials": _("Please enter a correct credentials"),
    }

    class Meta:
        model = UserModel
        fields = [*UserModel.AUTHENTICATION_FIELDS]

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super(MultipleLoginForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = False

    def get_user(self):
        return self.user_cache

    def clean(self):
        password = self.cleaned_data.pop('password')
        remember_me = self.cleaned_data.pop('remember_me')

        if not password:
            raise ValidationError(self.error_messages['invalid_credentials'],
                                  code='invalid_credentials')

        login_by = next((key for key in list(self.cleaned_data.keys()) if self.cleaned_data[key]), None)

        if login_by not in UserModel.AUTHENTICATION_FIELDS:
            raise ValidationError(
                self.error_messages['invalid_credentials'],
                code='invalid_credentials')

        credentials = {"password": password}

        credentials.update({login_by: self.cleaned_data[login_by]})
        if login_by and password:
            self.user_cache = authenticate(request=self.request, **credentials)
            if not self.user_cache:
                raise ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login')
            if not remember_me and self.request:
                self.request.session.set_expiry(0)
                self.request.session.modified = True
            else:
                if not self.user_cache.is_active:
                    raise ValidationError(self.error_messages['inactive'], code='inactive')

        return self.cleaned_data


class VerifyPhoneForm(forms.Form):
    code = forms.CharField(max_length=6, min_length=6)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(VerifyPhoneForm, self).__init__(*args, **kwargs)
        self.fields['code'].label = "message sent to phone number: {}".format(self.user.phone)

    def clean(self):
        code = self.cleaned_data.get('code')

        success = VerifyPhone().check(self.user.phone, code)
        if not success:
            raise ValidationError(_("The Provided code is Properly invalid"), code='invalid_code')

        return self.cleaned_data


# profile forms


class UserChangeForm(BaseUserChangeForm):
    class Meta(BaseUserChangeForm.Meta):
        model = UserModel

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UpdateUserDataForm(UserChangeForm):
    class Meta:
        model = UserModel
        fields = ('first_name', 'last_name')

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', None)
        if not first_name:
            raise ValidationError(_("Please Enter the new first"), code="required")

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name:
            raise ValidationError("Please Enter the last name", code="required")

        return last_name


class UpdateEmailForm(forms.Form):
    new_email = forms.EmailField(required=True, label=_("New Email"))
    password = forms.CharField(required=True,
                               label=_("Password"),
                               strip=False,
                               widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
                               )

    error_messages = {
        'invalid_login': _(
            "Please enter a correct phone and password. Note that both "
            "fields may be case-sensitive."
        )
    }

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(UpdateEmailForm, self).__init__(*args, **kwargs)

    def clean_new_email(self):
        old_email = self.user.email
        email = self.cleaned_data.get('new_email')

        if UserModel.objects.filter(email=email).exists():
            raise ValidationError(_("Email already exists"), code="unique")

        if old_email == email:
            raise ValidationError(_("Please Enter the new Email"), code="email_mismatch")

        return email

    def clean_password(self):
        username = self.user.email
        password = self.cleaned_data.get('password')

        credentials = {"password": password}
        credentials.update({UserModel.EMAIL_FIELD: username})

        if not authenticate(**credentials):
            raise ValidationError(_("Please Enter Valid Password"), code="invalid")

        return password

    def save(self, commit=True):
        email = self.cleaned_data["new_email"]
        self.user.email = email
        if commit:
            self.user.save()
        return self.user


class UpdatePhoneNumberForm(forms.Form):
    new_phone = forms.CharField(required=True)
    password = forms.CharField(
        label=_("Your Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )

    error_messages = {
        'invalid_login': _(
            "Please enter a correct phone and password. Note that both "
            "fields may be case-sensitive."
        )
    }

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(UpdatePhoneNumberForm, self).__init__(*args, **kwargs)
        self.phone_field = UserModel._meta.get_field(UserModel.REQUIRED_FIELDS[0])

    def clean_new_phone(self):
        phone = self.cleaned_data['new_phone']
        if UserModel.objects.filter(phone=phone).exists():
            raise ValidationError("Phone already exists", code="unique")
        return phone

    def clean(self):
        phone = self.user.phone
        password = self.cleaned_data.get('password')
        credentials = {"password": password}

        credentials.update({"phone": phone})

        if phone and password:
            authenticated_user = authenticate(**credentials)

        return self.cleaned_data

    def save(self, commit=True):
        phone = self.cleaned_data["new_phone"]
        self.user.phone = phone
        if commit:
            self.user.save()
        return self.user
