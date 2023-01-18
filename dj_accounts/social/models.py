from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext as _

UserModel = get_user_model()


class SocialProvider(models.Model):
    name = models.CharField(max_length=255, default=None, null=True, blank=True, verbose_name=_("Name"))
    logo = models.FileField(verbose_name=_("Logo"))
    default_provider = models.BooleanField(default=False, verbose_name=_("Default Provider"))
    provider = models.CharField(max_length=255,
                                choices=settings.SOCIAL_AUTHENTICATION_PROVIDERS,
                                default=settings.DEFAULT_SOCIAL_AUTHENTICATION_PROVIDER,
                                verbose_name=_("Provider"))
    client_id = models.CharField(max_length=500, verbose_name=_("Client Id"))
    client_secret = models.TextField(_("Client Secret"), null=True, blank=True, default=None)
    is_active = models.BooleanField(default=True)

    def get_provider(self):
        return dict(settings.SOCIAL_AUTHENTICATION_PROVIDERS).get(self.provider)


class SocialAccount(models.Model):
    provider = models.ForeignKey(SocialProvider, on_delete=models.CASCADE, verbose_name=_("Provider"))
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name="social_accounts",
                             verbose_name=_("User"))
    token = models.TextField(verbose_name=_("Token"))
    expires_at = models.DateTimeField(verbose_name=_("Expires At"))
    provider_user_id = models.BigIntegerField(_("Provider User ID"))
    is_active = models.BooleanField(default=False)
