import inspect
from unittest.mock import MagicMock, patch, Mock

from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import APIView

from ..factories import UserFactory
from ...mixins import RegisterMixin
from ...views_api import RegisterAPIView


class RegisterAPIViewStructureTestCase(APITestCase):
    def test_it_extends_drf_APIView(self):
        self.assertTrue(issubclass(RegisterAPIView, APIView))

    def test_it_extends_RegisterGetFormClassMixin(self):
        self.assertTrue(issubclass(RegisterAPIView, RegisterMixin))

    def test_authentication_classes_is_empty(self):
        self.assertEquals(len(RegisterAPIView.authentication_classes), 0)

    def test_permission_classes_is_empty(self):
        self.assertEquals(len(RegisterAPIView.permission_classes), 0)

    def test_it_has_post_method(self):
        self.assertIn('post', dict(inspect.getmembers(RegisterAPIView)))

    def test_post_method_is_callable(self):
        self.assertTrue(callable(RegisterAPIView.post))

    def test_post_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(RegisterAPIView.post)[0]
        self.assertEquals(actual_signature, expected_signature)


class RegisterAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.url = reverse('api_register')
        self.data = {
            "first_name": "Test",
            "last_name": "User",
            "phone": "01212105162",
            "email": "test@test.test",
            "username": "TestUser",
            "password1": "newTESTPasswordD",
            "password2": "newTESTPasswordD",
            "toc": True
        }

    def test_it_returns_422_when_data_is_invalid(self):
        response = self.client.post(self.url, {})
        self.assertEquals(response.status_code, 422)

    def test_it_returns_201_when_user_created_successfully(self):
        response = self.client.post(self.url, self.data)
        self.assertEquals(response.status_code, 201)

    @patch('dj_accounts.authentication.mixins.ViewCallbackMixin.get_callback', autospec=True)
    def test_it_calls_get_callback(self, mock_get_callback):
        self.client.post(self.url, self.data)
        self.assertTrue(mock_get_callback.called)

    @patch('dj_accounts.authentication.mixins.RegisterMixin.send_email_verification', autospec=True)
    def test_it_calls_send_mail_verification_function(self, mock_send_email_verification):
        self.client.post(self.url, self.data)
        self.assertTrue(mock_send_email_verification.called)

    @patch('dj_accounts.authentication.mixins.RegisterMixin.send_phone_verification', autospec=True)
    def test_it_calls_send_phone_verification_function(self, mock_send_phone_verification):
        self.client.post(self.url, self.data)
        self.assertTrue(mock_send_phone_verification.called)

    @patch('rest_framework_simplejwt.tokens.RefreshToken.for_user', autospec=True)
    def test_it_calls_refresh_token_for_user_method(self, mock_refresh_token_for_user):
        self.client.post(self.url, self.data)
        self.assertTrue(mock_refresh_token_for_user.called)

    def test_it_return_access_and_refresh_tokens_once_user_is_signup(self):
        response = self.client.post(self.url, self.data)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
