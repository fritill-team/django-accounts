import inspect

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import APIView

from dj_accounts.authentication.mixins import LoginGetFormClassMixin
from dj_accounts.authentication.tests.factories import UserFactory
from dj_accounts.authentication.views_api import LoginAPIView


class LoginAPIViewStructureTestCase(APITestCase):
    def test_it_extends_drf_api_view(self):
        self.assertTrue(issubclass(LoginAPIView, APIView))

    def test_it_extends_get_form_class_mixin(self):
        self.assertTrue(issubclass(LoginAPIView, LoginGetFormClassMixin))

    def test_authentication_classes_is_empty(self):
        self.assertEquals(len(LoginAPIView.authentication_classes), 0)

    def test_permission_classes_is_empty(self):
        self.assertEquals(len(LoginAPIView.permission_classes), 0)

    def test_it_has_post_method(self):
        self.assertIn('post', dict(inspect.getmembers(LoginAPIView)))

    def test_post_method_is_callable(self):
        self.assertTrue(callable(LoginAPIView.post))

    def test_post_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(LoginAPIView.post)[0]
        self.assertEquals(actual_signature, expected_signature)


class LoginAPIViewPOSTTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory(
            username="TestUser",
            email="testuser@mail.com",
        )
        self.url = reverse("api_login")

    def test_it_returns_user_tokens_on_success(self):
        response = self.client.post(self.url, {
            "identifier": self.user.email,
            "password": "secret"
        })
        self.assertIn("access_token", response.data)
        self.assertIn("refresh_token", response.data)

    def test_it_returns_status_code_200_on_success(self):
        response = self.client.post(self.url, {
            "identifier": self.user.email,
            "password": "secret"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_it_returns_validation_errors_on_failure(self):
        response = self.client.post(self.url, {})
        self.assertIn('identifier', response.data.keys())
        self.assertIn('password', response.data.keys())

    def test_it_returns_status_code_422_on_failure(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
