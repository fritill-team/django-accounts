import inspect
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.timezone import now
from django.views import View

from ..factories import UserFactory
from ...mixins import ViewCallbackMixin
from ...views import VerifyPhoneView


class VerifyPhoneViewStructureTestCase(TestCase):
    def test_it_extends_django_view_class(self):
        self.assertTrue(issubclass(VerifyPhoneView, View))

    def test_it_extends_login_required_mixin(self):
        self.assertTrue(issubclass(VerifyPhoneView, LoginRequiredMixin))

    def test_it_extends_ViewCallbackMixin_mixin(self):
        self.assertTrue(issubclass(VerifyPhoneView, ViewCallbackMixin))

    def test_view_has_method_get(self):
        self.assertTrue(hasattr(VerifyPhoneView, 'get'))

    def test_view_has_method_get_is_callable(self):
        self.assertTrue(callable(VerifyPhoneView.get))

    def test_get_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(VerifyPhoneView.get)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_view_has_method_post(self):
        self.assertTrue(hasattr(VerifyPhoneView, 'post'))

    def test_view_has_method_post_is_callable(self):
        self.assertTrue(callable(VerifyPhoneView.post))

    def test_post_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(VerifyPhoneView.post)[0]
        self.assertEquals(actual_signature, expected_signature)


class VerifyPhoneViewGETTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.url = reverse('verify-phone')

    def test_it_redirects_to_login_if_user_is_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("login") + "?next=" + self.url, fetch_redirect_response=False)

    def test_it_redirects_to_settings_login_redirect_url_if_phone_is_verified(self):
        self.user.phone_verified_at = now()
        self.user.save()
        response = self.client.get(self.url)
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False)

    def test_it_returns_verify_phone_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "dj_accounts/authentication/themes/corporate/verify_phone.html")

    def test_it_returns_form_in_response_context(self):
        response = self.client.get(self.url)
        self.assertIn('form', response.context)


class VerifyPhoneViewPOSTTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory(phone="201002536987")
        self.client.force_login(self.user)
        self.url = reverse('verify-phone')
        self.data = {"code": "777777"}

    def test_it_redirects_to_login_if_user_is_not_logged_in(self):
        self.client.logout()
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("login") + "?next=" + self.url, fetch_redirect_response=False)

    def test_it_redirects_to_settings_login_redirect_url_if_phone_is_verified(self):
        user = UserFactory(phone_verified_at=now())
        self.client.force_login(user)
        response = self.client.post(self.url)
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False)

    @patch('dj_accounts.authentication.mixins.ViewCallbackMixin.get_callback', autospec=True)
    def test_it_calls_get_callback_on_success(self, mocked_method):
        self.client.post(self.url, self.data)
        self.assertTrue(mocked_method.called)

    def test_it_updates_phone_verified_at_column_in_user_model_to_now_on_success(self):
        self.client.post(self.url, self.data)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.phone_verified_at)

    def test_it_redirects_to_phone_verification_complete_on_success(self):
        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False)

    def test_it_returns_verify_phone_template_on_failure(self):
        response = self.client.post(self.url)
        self.assertTemplateUsed(response, "dj_accounts/authentication/themes/corporate/verify_phone.html")

    def test_it_returns_form_in_response_context_on_failure(self):
        response = self.client.post(self.url)
        self.assertIn('form', response.context)
