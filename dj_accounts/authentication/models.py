from django import forms
from django.contrib.sites.models import Site
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from translation.models import TranslatableModel


class SiteProfile(TranslatableModel):
    translatable = {
        "name": {"field": forms.CharField},
        "address": {"field": forms.CharField, "widget": forms.Textarea},
        "copyrights": {"field": forms.CharField, "widget": forms.Textarea},
        "description": {"field": forms.CharField, "widget": forms.Textarea},
        "keywords": {"field": forms.CharField, "widget": forms.Textarea},
    }

    class Meta:
        verbose_name = _("Site Profile")
        verbose_name_plural = _('Sites Profiles')
        default_permissions = ()

    def upload_logo_to(self, filename):
        return 'sites/{}/{}'.format(self.site_id, filename)

    site = models.OneToOneField(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("Site"))
    name = models.JSONField(default=dict, verbose_name=_("Name"))
    description = models.JSONField(default=dict, verbose_name=_("Description"))
    address = models.JSONField(default=dict, verbose_name=_("Address"))
    copyrights = models.JSONField(default=dict, verbose_name=_("Copyrights"))
    keywords = models.JSONField(default=dict, verbose_name=_("Keywords"))
    logo = models.FileField(default=None, null=True, blank=True, upload_to=upload_logo_to, verbose_name=_("Logo"))

    def __str__(self):
        return self.translated_name


@receiver(post_save, sender=Site)
def create_site_profile_created_site_signal(sender, instance, created, **kwargs):
    if created:
        instance.siteprofile = SiteProfile.objects.create(
            site=instance,
            name=instance.name)
