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

    def test_it_called_send_mail_confirmation_function(self):
        response = self.client.post(self.url, self.data)
        response.mock = MagicMock()
        response.mock.send_mail_confirmation()
        response.mock.send_mail_confirmation.assert_called_once_with()

    @patch('dj_accounts.authentication.mixins.RegisterMixin.get_register_callback', autospec=True)
    def test_it_calls_get_register_callback(self, mock_get_register_callback):
        self.client.post(self.url, self.data)
        self.assertTrue(mock_get_register_callback.called)

    @patch('dj_accounts.authentication.mixins.RegisterMixin.call_send_email_confirmation', autospec=True)
    def test_it_calls_call_send_mail_confirmation_function(self, mock_call_send_email_confirmation):
        self.client.post(self.url, self.data)
        self.assertTrue(mock_call_send_email_confirmation.called)

    # def test_it_create_send_the_email(self):
    #     response = self.client.post(self.url, self.data)
    #     self.assertEqual(len(mail.outbox), 1)
    #     self.assertEqual(mail.outbox[0].subject, 'Activate your account.')

    def test_it_return_access_and_refresh_tokens_once_user_is_signup(self):
        response = self.client.post(self.url, self.data)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
