import inspect
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.views import View

from ...forms import RegisterForm
from ...mixins import RegisterMixin
from ...tests.factories import UserFactory
from ...views import RegisterView


class RegisterViewStructureTestCase(TestCase):
    def test_it_extends_django_view_class(self):
        self.assertTrue(issubclass(RegisterView, View))

    def test_it_extends_register_get_form_class_mixin(self):
        self.assertTrue(issubclass(RegisterView, RegisterMixin))

    def test_view_has_method_get(self):
        self.assertTrue(hasattr(RegisterView, 'get'))

    def test_view_has_method_get_is_callable(self):
        self.assertTrue(callable(RegisterView.get))

    def test_get_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(RegisterView.get)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_view_has_method_post(self):
        self.assertTrue(hasattr(RegisterView, 'post'))

    def test_view_has_method_post_is_callable(self):
        self.assertTrue(callable(RegisterView.post))

    def test_post_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(RegisterView.post)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_view_has_method_get_template_name(self):
        self.assertTrue(hasattr(RegisterView, 'get_template_name'))

    def test_view_has_method_get_template_name_is_callable(self):
        self.assertTrue(callable(RegisterView.get_template_name))

    def test_get_template_name_method_signature(self):
        expected_signature = ['self']
        actual_signature = inspect.getfullargspec(RegisterView.get_template_name)[0]
        self.assertEquals(actual_signature, expected_signature)


class RegisterViewGetTemplateNameTestCase(TestCase):
    @override_settings(AUTHENTICATION_THEME='creative')
    def test_it_returns_template_name_based_on_settings_authentication_theme_option(
            self):
        template_name = RegisterView().get_template_name()
        self.assertEquals('dj_accounts/authentication/themes/creative/register.html', template_name)


class RegisterViewGETTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('register')

    def test_it_redirects_to_settings_login_redirect_url_if_user_is_logged_in(self):
        self.client.force_login(UserFactory())
        response = self.client.get(self.url)
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False)

    def test_it_returns_register_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'dj_accounts/authentication/themes/corporate/register.html')

    def test_it_returns_form_in_response_context(self):
        response = self.client.get(self.url)
        self.assertIn('form', response.context)

    @override_settings(REGISTER_FORM=RegisterForm)
    def test_response_context_form_is_instance_of_register_form_if_settings_register_from_is_set(self):
        response = self.client.get(self.url)
        self.assertIsInstance(response.context['form'], RegisterForm)


class RegisterViewPOSTTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('register')
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

    def test_it_redirects_to_settings_login_redirect_url_if_user_is_logged_in(self):
        user = UserFactory()
        self.client.login(email=user.email, password="secret")
        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False)

    def test_it_creates_user_with_provided_data(self):
        self.client.post(self.url, self.data)
        self.assertTrue(get_user_model().objects.filter(username="TestUser").exists())

    def test_it_logs_in_the_created_user(self):
        self.client.post(self.url, self.data)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEquals(self.client.session['_auth_user_id'],
                          str(get_user_model().objects.get(username="TestUser").id))

    @override_settings(LOGIN_REDIRECT_URL="/dj_accounts/login/")
    def test_it_redirect_to_next_if_next_in_request(self):
        self.data.update({"next": '/'})
        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, '/', fetch_redirect_response=False)

    def test_it_redirects_to_settings_login_redirect_url_if_next_is_not_provided(self):
        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False)

    def test_it_returns_register_template_if_form_is_invalid(self):
        response = self.client.post(self.url)
        self.assertTemplateUsed(response, 'dj_accounts/authentication/themes/corporate/register.html')

    def test_it_returns_form_in_response_context_if_form_is_invalid(self):
        response = self.client.post(self.url)
        self.assertIn('form', response.context)

    @override_settings(REGISTER_FORM=RegisterForm)
    def test_response_context_form_is_instance_of_register_form_if_settings_register_from_is_set(self):
        response = self.client.get(self.url)
        self.assertIsInstance(response.context['form'], RegisterForm)

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