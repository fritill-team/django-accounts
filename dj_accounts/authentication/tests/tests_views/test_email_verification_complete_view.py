import inspect

from django.test import TestCase, Client
from django.urls import reverse
from django.views import View

from ..factories import UserFactory
from ...views import EmailVerificationCompleteView


class EmailVerificationCompleteViewStructureTestCase(TestCase):
    def test_it_extends_django_view_class(self):
        self.assertTrue(issubclass(EmailVerificationCompleteView, View))

    def test_view_has_method_get(self):
        self.assertTrue(hasattr(EmailVerificationCompleteView, 'get'))

    def test_view_has_method_get_is_callable(self):
        self.assertTrue(callable(EmailVerificationCompleteView.get))

    def test_get_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(EmailVerificationCompleteView.get)[0]
        self.assertEquals(actual_signature, expected_signature)


class EmailVerificationCompleteViewGETTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.url = reverse('email-verification-complete')

    def test_it_returns_email_verification_complete_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(
            response,
            "dj_accounts/authentication/themes/corporate/email_verification_complete.html")

    def test_it_returns_verified_in_context(self):
        response = self.client.get(self.url)
        self.assertIn('verified', response.context)
        self.assertEqual(response.context['verified'], self.user.email_verified_at)
