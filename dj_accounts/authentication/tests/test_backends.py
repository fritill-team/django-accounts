from django.test import TestCase, override_settings, Client

from .factories import UserFactory


class MultipleAuthenticationBackendTestCase(TestCase):
    @override_settings(AUTHENTICATION_BACKENDS=["dj_accounts.authentication.backends.MultipleAuthenticationBackend"])
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()

    def test_logs_in_with_identifier_and_password(self):
        self.client.login(identifier=self.user.username, password="secret")
        self.assertIn("sessionid", self.client.cookies)

    def test_it_fails_if_password_is_not_provided(self):
        self.client.login(identifier=self.user.email)
        self.assertNotIn("sessionid", self.client.cookies)

    def test_it_fails_if_identifier_is_not_provided(self):
        self.client.login(password="secret")
        self.assertNotIn("sessionid", self.client.cookies)

    def test_it_fails_if_password_is_not_correct(self):
        self.client.login(email=self.user.email, password="not a correct password")
        self.assertNotIn("sessionid", self.client.cookies)

    def test_it_fails_if_user_is_not_active(self):
        self.user.is_active = False
        self.user.save()
        self.client.login(email=self.user.email, password="secret")
        self.assertNotIn("sessionid", self.client.cookies)

    def test_it_fails_if_user_does_not_exists(self):
        self.client.login(email="doesnotexist@mail.com", password="secret")
        self.assertNotIn("sessionid", self.client.cookies)
