import inspect
from unittest.mock import patch

from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import APIView

from .. import authenticate_api_user
from ..factories import UserFactory
from ...mixins import ViewCallbackMixin, SendEmailVerificationMixin
from ...views_api import ResendEmailVerificationLinkAPIView


class ResendEmailVerificationLinkAPIViewStructureTestCase(APITestCase):
    def test_it_extends_APIView_class(self):
        self.assertTrue(issubclass(ResendEmailVerificationLinkAPIView, APIView))

    def test_it_extends_ViewCallbackMixin_class(self):
        self.assertTrue(issubclass(ResendEmailVerificationLinkAPIView, ViewCallbackMixin))

    def test_it_extends_SendEmailVerificationMixin_class(self):
        self.assertTrue(issubclass(ResendEmailVerificationLinkAPIView, SendEmailVerificationMixin))

    def test_view_has_method_get(self):
        self.assertTrue(hasattr(ResendEmailVerificationLinkAPIView, 'get'))

    def test_view_has_method_get_is_callable(self):
        self.assertTrue(callable(ResendEmailVerificationLinkAPIView.get))

    def test_get_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(ResendEmailVerificationLinkAPIView.get)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_it_has_IsAuthenticated_in_permission_classes(self):
        self.assertIn(IsAuthenticated, ResendEmailVerificationLinkAPIView.permission_classes)


class ResendEmailVerificationLinkAPIViewGETTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = authenticate_api_user(APIClient(), self.user)
        self.url = reverse("api_resend_email_verification")

    def test_it_returns_401_if_user_is_not_authenticated(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('dj_accounts.authentication.mixins.SendEmailVerificationMixin.send_email_verification', autospec=True)
    def test_it_calls_send_mail_verification_function(self, mock_send_email_verification):
        self.client.get(self.url)
        self.assertTrue(mock_send_email_verification.called)

    @patch('dj_accounts.authentication.mixins.ViewCallbackMixin.get_callback', autospec=True)
    def test_it_calls_get_callback(self, mock_get_callback):
        self.client.get(self.url)
        self.assertTrue(mock_get_callback.called)

    def test_it_returns_200_on_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_it_returns_message_on_response_data_on_success(self):
        response = self.client.get(self.url)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], _('Email activation link sent successfully'))
