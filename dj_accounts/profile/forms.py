from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm

UserModel = get_user_model()


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