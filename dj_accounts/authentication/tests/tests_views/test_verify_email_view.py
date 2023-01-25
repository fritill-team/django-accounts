import inspect
from unittest.mock import patch, Mock

from django.test import TestCase, Client
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View

from dj_accounts.utils import account_activation_token
from ..factories import UserFactory
from ...mixins import VerifyEmailMixin, ViewCallbackMixin
from ...views import VerifyEmailView


class VerifyEmailViewStructureTestCase(TestCase):
    def test_it_extends_django_view_class(self):
        self.assertTrue(issubclass(VerifyEmailView, View))

    def test_it_extends_VerifyEmailMixin_class(self):
        self.assertTrue(issubclass(VerifyEmailView, VerifyEmailMixin))

    def test_it_extends_ViewCallbackMixin_class(self):
        self.assertTrue(issubclass(VerifyEmailView, ViewCallbackMixin))

    def test_it_has_get_method(self):
        self.assertIn('get', dict(inspect.getmembers(VerifyEmailView)))

    def test_get_is_callable(self):
        self.assertTrue(callable(VerifyEmailView.get))

    def test_get_method_signature(self):
        expected_signature = ['self', 'request', 'uidb64', 'token']
        actual_signature = inspect.getfullargspec(VerifyEmailView.get)[0]
        self.assertEquals(actual_signature, expected_signature)


class VerifyEmailViewGETTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = account_activation_token.make_token(self.user)
        self.url = reverse('verify-email', args=[self.uid, self.token])

    @patch('dj_accounts.authentication.mixins.VerifyEmailMixin.verify', autospec=True, return_value=[Mock(), Mock()])
    def test_it_calls_verify_method(self, mocked_method):
        self.client.get(self.url)
        self.assertTrue(mocked_method.called)

    @patch('dj_accounts.authentication.mixins.ViewCallbackMixin.get_callback', autospec=True)
    def test_it_calls_get_callback_method(self, mocked_method):
        self.client.get(self.url)
        self.assertTrue(mocked_method.called)

    def test_it_redirects_to_email_verification_success_view(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('email-verification-complete'))
