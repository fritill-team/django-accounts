import inspect
from unittest.mock import patch, Mock

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import APIView

from dj_accounts.utils import account_activation_token
from .. import authenticate_api_user
from ..factories import UserFactory
from ...mixins import VerifyEmailMixin, ViewCallbackMixin
from ...views_api import VerifyEmailAPIView


class VerifyEmailAPIViewStructureTestCase(APITestCase):
    def test_it_extends_APIView_class(self):
        self.assertTrue(issubclass(VerifyEmailAPIView, APIView))

    def test_it_extends_VerifyEmailMixin_class(self):
        self.assertTrue(issubclass(VerifyEmailAPIView, VerifyEmailMixin))

    def test_it_extends_ViewCallbackMixin_class(self):
        self.assertTrue(issubclass(VerifyEmailAPIView, ViewCallbackMixin))

    def test_it_has_get_method(self):
        self.assertIn('get', dict(inspect.getmembers(VerifyEmailAPIView)))

    def test_get_is_callable(self):
        self.assertTrue(callable(VerifyEmailAPIView.get))

    def test_get_method_signature(self):
        expected_signature = ['self', 'request', 'uidb64', 'token']
        actual_signature = inspect.getfullargspec(VerifyEmailAPIView.get)[0]
        self.assertEquals(actual_signature, expected_signature)


class VerifyEmailAPIViewGETTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = authenticate_api_user(APIClient(), self.user)
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = account_activation_token.make_token(self.user)
        self.url = reverse('api_verify_email', args=[self.uid, self.token])
        self.fail_url = reverse('api_verify_email', args=['not-valid', 'not-valid'])

    @patch('dj_accounts.authentication.mixins.VerifyEmailMixin.verify', autospec=True, return_value=[Mock(), Mock()])
    def test_it_calls_verify_method(self, mocked_method):
        self.client.get(self.url)
        self.assertTrue(mocked_method.called)

    @patch('dj_accounts.authentication.mixins.ViewCallbackMixin.get_callback', autospec=True)
    def test_it_calls_get_callback_method(self, mocked_method):
        self.client.get(self.url)
        self.assertTrue(mocked_method.called)

    def test_it_return_200_status_code_on_success(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_message_on_success(self):
        response = self.client.get(self.url)
        self.assertEquals(response.data['message'], _('Email was verified successfully.'))

    def test_it_return_400_status_code_on_failure(self):
        response = self.client.get(self.fail_url)
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_message_value_on_failure(self):
        response = self.client.get(self.fail_url)
        self.assertEquals(response.data['message'], _('Something went wrong, please try again!'))
