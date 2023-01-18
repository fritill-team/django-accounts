from datetime import datetime

from django import forms
from django.utils.timezone import make_aware

from dj_accounts.models import SocialProvider


class SocialProviderForm(forms.ModelForm):
    class Meta:
        model = SocialProvider
        fields = ("name", "provider", "client_id", "client_secret", "default_provider", "is_active", 'logo')


class FacebookTokenForm(forms.Form):
    token = forms.CharField(required=True)
    userId = forms.IntegerField(required=True)
    expires = forms.IntegerField(required=True)
    applicationId = forms.IntegerField(required=True)
    name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    image = forms.ImageField(required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    gender = forms.CharField(required=False)
    birthdate = forms.DateTimeField(required=False)
    phone = forms.CharField(required=False)

    def clean(self):
        cleaned_data = self.cleaned_data
        cleaned_data['expires'] = make_aware(datetime.fromtimestamp(cleaned_data['expires'] / 1000.0))

        if 'first_name' not in cleaned_data or 'last_name' not in cleaned_data:
            username = cleaned_data['name'].split(" ")
            cleaned_data['first_name'] = username[0]
            cleaned_data['last_name'] = ' '.join(username[1:])

        if 'birthdate' not in cleaned_data:
            cleaned_data['birthdate'] = None

        return cleaned_data
