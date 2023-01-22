from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import View


class SiteListView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ('')
