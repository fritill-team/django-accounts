from django.test import TestCase
from django.urls import resolve, reverse

from ..views import ChangeEmailView, ChangePhoneView, UpdateProfileView


class ProfileUrlsTestCase(TestCase):
    def test_change_email_url_resolves(self):
        url = reverse("change-email")
        self.assertEquals(resolve(url).func.view_class, ChangeEmailView)

    def test_change_phone_url_resolves(self):
        url = reverse("change-phone")
        self.assertEquals(resolve(url).func.view_class, ChangePhoneView)

    def test_update_profile_url_resolves(self):
        url = reverse("update-profile")
        self.assertEquals(resolve(url).func.view_class, UpdateProfileView)
