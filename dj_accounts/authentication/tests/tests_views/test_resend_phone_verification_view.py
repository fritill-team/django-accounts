import inspect
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.test import TestCase, Client
from django.urls import reverse
from django.views import View

from ..factories import UserFactory
from ...mixins import SendPhoneVerificationMixin, ViewCallbackMixin
from ...views import ResendPhoneVerificationView

UserModel = get_user_model()


class ResendPhoneVerificationViewStructureTestCase(TestCase):
    def test_it_extends_django_view_class(self):
        self.assertTrue(issubclass(ResendPhoneVerificationView, View))

    def test_it_extends_login_required_mixin(self):
        self.assertTrue(issubclass(ResendPhoneVerificationView, LoginRequiredMixin))

    def test_it_extends_SendPhoneVerificationMixin_mixin(self):
        self.assertTrue(issubclass(ResendPhoneVerificationView, SendPhoneVerificationMixin))

    def test_it_extends_ViewCallbackMixin_mixin(self):
        self.assertTrue(issubclass(ResendPhoneVerificationView, ViewCallbackMixin))

    def test_view_has_method_get(self):
        self.assertTrue(hasattr(ResendPhoneVerificationView, 'get'))

    def test_view_has_method_get_is_callable(self):
        self.assertTrue(callable(ResendPhoneVerificationView.get))

    def test_get_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(ResendPhoneVerificationView.get)[0]
        self.assertEquals(actual_signature, expected_signature)


class ResendPhoneVerificationViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.url = reverse("resend_phone_activation")

    @patch('dj_accounts.authentication.mixins.SendPhoneVerificationMixin.send_phone_verification', autospec=True)
    def test_it_calls_resend_phone_verification_method(self, mocked_method):
        self.client.get(self.url)
        self.assertTrue(mocked_method.called)

    @patch('dj_accounts.authentication.mixins.ViewCallbackMixin.get_callback', autospec=True)
    def test_it_calls_get_callback_method(self, mocked_method):
        self.client.get(self.url)
        self.assertTrue(mocked_method.called)

    def test_it_redirects_to_login_if_user_is_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("login") + "?next=" + self.url)

    def test_it_redirect_to_phone_verification_again(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("verify-phone"))
