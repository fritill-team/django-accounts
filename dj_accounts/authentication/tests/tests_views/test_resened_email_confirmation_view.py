import inspect
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.test import TestCase, Client
from django.urls import reverse
from django.views import View

from ..factories import UserFactory
from ...mixins import SendEmailVerificationMixin
from ...views import ResendEmailVerificationLinkView


class ResendEmailVerificationLinkViewStructureTestCase(TestCase):
    def test_it_extends_django_view_class(self):
        self.assertTrue(issubclass(ResendEmailVerificationLinkView, View))

    def test_it_extends_login_required_mixin_class(self):
        self.assertTrue(issubclass(ResendEmailVerificationLinkView, LoginRequiredMixin))

    def test_it_extends_send_email_verification_mixin_class(self):
        self.assertTrue(issubclass(ResendEmailVerificationLinkView, SendEmailVerificationMixin))

    def test_view_has_method_get(self):
        self.assertTrue(hasattr(ResendEmailVerificationLinkView, 'get'))

    def test_view_has_method_get_is_callable(self):
        self.assertTrue(callable(ResendEmailVerificationLinkView.get))

    def test_get_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(ResendEmailVerificationLinkView.get)[0]
        self.assertEquals(actual_signature, expected_signature)


class ResendEmailVerificationLinkViewGETTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.client.force_login(UserFactory(is_superuser=True))
        self.url = reverse('resend-email-verification') + '?next=/'

    @patch('dj_accounts.authentication.mixins.SendEmailVerificationMixin.send_email_verification', autospec=True)
    def test_it_calls_send_mail_verification_function(self, mock_send_email_verification):
        self.client.get(self.url)
        self.assertTrue(mock_send_email_verification.called)

    def test_it_redirects_to_the_passed_url_in_next_parameter(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, '/', fetch_redirect_response=False)

    def test_it_redirects_to_login_redirect_url_if_next_is_not_present(self):
        response = self.client.get(reverse('resend-email-verification'))
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False)

    @patch('dj_accounts.authentication.mixins.ViewCallbackMixin.get_callback', autospec=True)
    def test_it_calls_get_callback(self, mock_get_callback):
        self.client.get(reverse('resend-email-verification'))
        self.assertTrue(mock_get_callback.called)
