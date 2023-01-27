import inspect

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .factories import UserFactory
from ..serializers import ChangePasswordSerializer
from ..views_api import UpdateProfileAPIView, VerifyPhoneAPIView, ResendPhoneVerificationAPIView, \
    UserLogoutAPIView, ChangePasswordAPIView


# class LoginAPIViewTestCase(TestCase):
#     def setUp(self):
#         self.url = reverse('api-v1:login')
#         self.user = UserFactory()
#         self.client = APIClient()
#
#     def test_it_return_401_if_not_active_user_tried_to_authenticate(self):
#         self.user.is_active = False
#         self.user.save()
#         response = self.client.post(self.url, {'email': self.user.email, 'password': '123'})
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#
#     def test_it_return_401_if_user_does_not_exist(self):
#         response = self.client.post(self.url, {'email': 'not_exist', 'password': '123'})
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#
#     def test_it_return_401_if_password_is_wrong(self):
#         response = self.client.post(self.url, {'email': self.user.email, 'password': 'wrong'})
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#
#     def test_it_return_200_if_user_is_valid(self):
#         response = self.client.post(self.url, {'email': self.user.email, 'password': 'secret'})
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#     def test_it_return_access_token_after_user_is_authenticated_correctly(self):
#         response = self.client.post(self.url, {'email': self.user.email, 'password': 'secret'})
#         self.assertTrue('access' in response.data)
#
#     def test_it_return_refresh_token_after_user_is_authenticated_correctly(self):
#         response = self.client.post(self.url, {'email': self.user.email, 'password': 'secret'})
#         self.assertTrue('refresh' in response.data)
#
#     def test_it_return_401_if_invalid_token_was_given(self):
#         client = APIClient()
#         client.credentials(HTTP_AUTHORIZATION='Bearer ' + 'abc')
#         response = client.get(reverse('api-v1:verify-phone'))
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#
#     def test_the_returned_token_is_valid(self):
#         client = APIClient()
#         response = client.post(self.url, {'email': self.user.email, 'password': 'secret'})
#         self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
#         token = response.data['access']
#         client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(token))
#         response = client.get(reverse('api-v1:resend-email-activation'))
#         self.assertEqual(response.status_code, status.HTTP_200_OK)


# logout

class TestUserLogoutViewStructure(TestCase):
    def test_it_extends_api_view_class(self):
        self.assertTrue(issubclass(UserLogoutAPIView, APIView))

    def test_view_has_method_post(self):
        self.assertTrue(hasattr(UserLogoutAPIView, 'post'))

    def test_view_has_method_post_is_callable(self):
        self.assertTrue(callable(UserLogoutAPIView.post))

    def test_post_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(UserLogoutAPIView.post)[0]
        self.assertEquals(actual_signature, expected_signature)


class TestUserLogoutView(TestCase):
    @override_settings(MULTIPLE_AUTHENTICATION_ACTIVE=True)
    def setUp(self):
        self.url = reverse('api_login')
        self.user = UserFactory()
        self.client = APIClient()
        login_response = self.client.post(self.url, {'email': self.user.email, 'password': 'secret'})
        self.refresh = login_response.data['refresh_token']
        self.token = login_response.data['access_token']

    def test_it_return_401_if_user_not_logged_in(self):
        response = self.client.post(reverse('logout_api'), {'refresh': self.refresh})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_it_return_204_if_user_is_logged_out(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(self.token))
        response = self.client.post(reverse('logout_api'), {'refresh': self.refresh})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_it_return_400_if_invalid_token_was_given(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(self.token))
        response = self.client.post(reverse('logout_api'), {'refresh': 'abc'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)




class ResendPhoneVerificationViewStructureTestCase(TestCase):
    def test_it_extends_django_LoginView(self):
        self.assertTrue(issubclass(ResendPhoneVerificationAPIView, APIView))

    def test_it_permission_classes_has_is_authenticated(self):
        self.assertIn(IsAuthenticated, ResendPhoneVerificationAPIView.permission_classes)

    def test_view_has_method_get(self):
        self.assertTrue(hasattr(ResendPhoneVerificationAPIView, 'get'))

    def test_view_has_method_get_is_callable(self):
        self.assertTrue(callable(ResendPhoneVerificationAPIView.get))

    def test_get_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(ResendPhoneVerificationAPIView.get)[0]
        self.assertEquals(actual_signature, expected_signature)


class PhoneVerificationViewGETTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(self.refresh.access_token))
        self.url = reverse("resend_phone_activation_api")

    def test_it_returns_status_code_of_401_if_user_is_not_authenticated(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 401)

    def test_it_return_200_status_code_if_code_was_resent_successfully(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_response_message_value(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data['message'], _('Code was resent successfully.'))

