from django.conf import settings


def create_site_profile_for_initial_sites(sender, **kwargs):
    from django.contrib.sites.models import Site
    from dj_accounts.authentication.models import SiteProfile

    for site in Site.objects.filter(siteprofile__isnull=True):
        SiteProfile.objects.create(
            site=site,
            name={settings.FALLBACK_LOCALE: site.name}
        )


def create_site_profile_created_site_signal(sender, instance, created, **kwargs):
    if created:
        from dj_accounts.authentication.models import SiteProfile

        instance.siteprofile = SiteProfile.objects.create(
            site=instance,
            name=instance.name)
