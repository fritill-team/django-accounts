from django.apps import AppConfig
from django.db.models.signals import post_migrate


class DjAccountsAuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dj_accounts.authentication'

    def ready(self):
        from .signals import create_site_profile_for_initial_sites
        post_migrate.connect(create_site_profile_for_initial_sites, sender=self)
