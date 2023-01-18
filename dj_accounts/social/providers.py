from django.contrib.auth import get_user_model

from .forms import FacebookTokenForm
from ..models import SocialProvider, SocialAccount

UserModel = get_user_model()


class BaseProvider:
    form = None
    mapped_data = {
        "provider_user_id": None,
        "token": None,
        "expires_at": None,
        "username": None,
        "first_name": None,
        "last_name": None,
        "email": None,
        "image": None,
        "gender": None,
        "birthdate": None,
        "phone": None
    }
    user_data_fields = (
        "username", "first_name", "last_name", "email", "image", "gender", "birthdate", "phone"
    )
    social_account_fields = ("provider_user_id", "token", "expires_at")

    def __init__(self, data):
        if not self.__class__.__name__.endswith("Provider"):
            raise Exception("Provider name must end with \"Provider\"")

        if not self.form:
            raise Exception("You must define form class")

        self.provider_name = self.__class__.__name__.split('Provider')[0].lower()
        self.user_data = {}
        self.social_account_data = {}
        self.data = data
        self.provider = SocialProvider.objects.get(
            provider=self.provider_name,
            client_id=self.data.get(self.get_provider_map_value('client_id'))
        )

    def validate(self):
        form = self.form(data=self.data)
        if form.is_valid():
            print(form.cleaned_data)
            self.map_data(form.cleaned_data)
            return True, None
        return False, form.errors.as_data()

    def map_data(self, data):
        for item in self.user_data_fields:
            self.user_data[item] = data.get(self.get_provider_map_value(item))

        for item in self.social_account_fields:
            self.social_account_data[item] = data.get(self.get_provider_map_value(item))

    def get_provider_map_value(self, key):
        return self.mapped_data.get(key)

    def get_user(self):
        status, errors = self.validate()
        if not status:
            return status, errors

        user_account = SocialAccount.objects.filter(
            provider=self.provider,
            provider_user_id=self.social_account_data.get('user_id'),
        )
        new_account = False
        if user_account.exists():
            user = user_account.user
            user_account.update(is_active=False)
        else:
            user = UserModel.objects.filter(email=self.user_data.get('email'))

            if user.exists():
                user = user.first()
            else:
                user = UserModel.objects.create(**self.user_data)
                new_account = True

        user.social_accounts.create(
            provider=self.provider,
            is_active=True,
            **self.social_account_data
        )

        return True, user, new_account


class FacebookProvider(BaseProvider):
    form = FacebookTokenForm

    mapped_data = {
        "provider_user_id": "userId",
        "token": "token",
        "expires_at": "expires",
        "client_id": "applicationId",
        "username": "name",
        "first_name": "first_name",
        "last_name": "last_name",
        "email": "email",
        "image": "picture",
        "gender": "gender",
        "birthdate": "birthdate",
        "phone": "phone"
    }


class TwitterProvider(BaseProvider):
    pass


class GoogleProvider(BaseProvider):
    pass


SOCIAL_PROVIDERS = {
    "facebook": FacebookProvider,
    "twitter": TwitterProvider,
    "google": GoogleProvider
}


def get_provider(provider_name):
    return SOCIAL_PROVIDERS.get(provider_name)
