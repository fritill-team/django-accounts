import inspect
from unittest.mock import patch

from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext as _
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import APIView

from .. import authenticate_api_user
from ..factories import UserFactory
from ...mixins import ViewCallbackMixin
from ...views_api import VerifyPhoneAPIView


class VerifyPhoneAPIViewStructureTestCase(APITestCase):
    def test_it_extends_django_view_class(self):
        self.assertTrue(issubclass(VerifyPhoneAPIView, APIView))

    def test_it_extends_ViewCallbackMixin_class(self):
        self.assertTrue(issubclass(VerifyPhoneAPIView, ViewCallbackMixin))

    def test_it_has_IsAuthenticated_in_permission_classes(self):
        self.assertIn(IsAuthenticated, VerifyPhoneAPIView.permission_classes)

    def test_view_has_method_post(self):
        self.assertTrue(hasattr(VerifyPhoneAPIView, 'post'))

    def test_view_has_method_post_is_callable(self):
        self.assertTrue(callable(VerifyPhoneAPIView.post))

    def test_post_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(VerifyPhoneAPIView.post)[0]
        self.assertEquals(actual_signature, expected_signature)


class VerifyPhoneAPIViewPOSTTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory(phone="12312123")
        self.client = authenticate_api_user(APIClient(), self.user)
        self.url = reverse("verify_phone_api")
        self.data = {"code": "777777"}

    @patch('dj_accounts.authentication.mixins.ViewCallbackMixin.get_callback', autospec=True)
    def test_it_calls_get_callback_on_success(self, mocked_method):
        self.client.post(self.url, self.data)
        self.assertTrue(mocked_method.called)

    def test_it_return_401_status_code_if_user_is_not_logged_in(self):
        self.client.logout()
        response = self.client.post(self.url)
        self.assertEquals(response.status_code, 401)

    def test_it_return_200_if_user_is_verified(self):
        user = UserFactory(phone_verified_at=now())
        self.client.login(email=user.email, password="secret")
        response = self.client.post(self.url, self.data)
        self.assertEquals(response.status_code, 200)
        self.assertIn("message", response.data)
        self.assertEquals(_('Phone verified successfully!'), response.data['message'])

    def test_it_updates_phone_verified_at_column_in_user_model_to_now_on_success(self):
        self.client.post(self.url, self.data)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.phone_verified_at)

    def test_it_raise_422_status_code_for_invalid_data(self):
        self.data = {"code": ""}
        response = self.client.post(self.url, self.data)
        self.assertEquals(response.status_code, 422)

    def test_it_return_400_bad_request_user_was_verified_before(self):
        self.user.phone_verified_at = now()
        self.user.save()
        response = self.client.post(self.url, self.data)
        self.assertEquals(response.status_code, 400)
        self.assertIn("message", response.data)
        self.assertEquals(_('this account was activated before'), response.data['message'])
