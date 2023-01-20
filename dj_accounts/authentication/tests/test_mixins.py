import inspect
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.core import mail
from django.test import TestCase, override_settings, RequestFactory
from django.urls import reverse

from ..forms import MultipleLoginForm, RegisterForm, UserCreationForm
from ..mixins import LoginGetFormClassMixin, RegisterMixin
from ..tests.factories import UserFactory
from ..tests.forms import TestLoginForm


class LoginGetFormClassMixinTestCase(TestCase):
    def test_it_has_get_form_class_method(self):
        self.assertIn('get_form_class', dict(inspect.getmembers(LoginGetFormClassMixin)))

    def test_get_form_class_is_callable(self):
        self.assertTrue(callable(LoginGetFormClassMixin.get_form_class))

    def test_get_form_class_method_signature(self):
        expected_signature = ['self']
        actual_signature = inspect.getfullargspec(LoginGetFormClassMixin.get_form_class)[0]
        self.assertEquals(actual_signature, expected_signature)

    @override_settings(MULTIPLE_AUTHENTICATION_ACTIVE=True)
    def test_it_returns_phone_login_form_if_MULTIPLE_AUTHENTICATION_ACTIVE_is_true(self):
        self.assertTrue(issubclass(LoginGetFormClassMixin().get_form_class(), MultipleLoginForm))

    @override_settings(MULTIPLE_AUTHENTICATION_ACTIVE=False, LOGIN_FORM=None)
    def test_it_returns_default_login_form_if_MULTIPLE_AUTHENTICATION_ACTIVE_is_false_and_login_form_is_none(
            self):
        self.assertTrue(issubclass(LoginGetFormClassMixin().get_form_class(), AuthenticationForm))

    @override_settings(LOGIN_FORM='dj_accounts.authentication.tests.forms.TestLoginForm',
                       MULTIPLE_AUTHENTICATION_ACTIVE=False)
    def test_it_returns_settings_login_form_if_is_set(self):
        self.assertEquals(LoginGetFormClassMixin().get_form_class(), TestLoginForm)


class RegisterMixinStructureTestCase(TestCase):
    def test_it_has_get_form_class_method(self):
        self.assertIn('get_form_class', dict(inspect.getmembers(RegisterMixin)))

    def test_get_form_class_is_callable(self):
        self.assertTrue(callable(RegisterMixin.get_form_class))

    def test_get_form_class_method_signature(self):
        expected_signature = ['self']
        actual_signature = inspect.getfullargspec(RegisterMixin.get_form_class)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_it_has_get_register_callback_method(self):
        self.assertIn('get_register_callback', dict(inspect.getmembers(RegisterMixin)))

    def test_get_register_callback_is_callable(self):
        self.assertTrue(callable(RegisterMixin.get_register_callback))

    def test_get_register_callback_method_signature(self):
        expected_signature = ['self', 'user', 'delay']
        actual_signature = inspect.getfullargspec(RegisterMixin.get_register_callback)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_it_has_send_email_confirmation_method(self):
        self.assertIn('send_email_confirmation', dict(inspect.getmembers(RegisterMixin)))

    def test_send_email_confirmation_is_callable(self):
        self.assertTrue(callable(RegisterMixin.send_email_confirmation))

    def test_send_email_confirmation_method_signature(self):
        expected_signature = ['self', 'request', 'user']
        actual_signature = inspect.getfullargspec(RegisterMixin.send_email_confirmation)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_it_has_send_phone_verification_method(self):
        self.assertIn('send_phone_verification', dict(inspect.getmembers(RegisterMixin)))

    def test_send_phone_verification_is_callable(self):
        self.assertTrue(callable(RegisterMixin.send_phone_verification))

    def test_send_phone_verification_method_signature(self):
        expected_signature = ['self', 'user']
        actual_signature = inspect.getfullargspec(RegisterMixin.send_phone_verification)[0]
        self.assertEquals(actual_signature, expected_signature)


class RegisterMixinGetRegisterCallbackTestCase(TestCase):
    @override_settings(REGISTER_CALLBACK='dj_accounts.authentication.tests.mocks.register_callback')
    @patch('dj_accounts.authentication.tests.mocks.register_callback', autospec=True)
    def test_it_calls_settings_register_callback_if_is_set(self, mock_register_callback):
        RegisterMixin().get_register_callback(UserFactory())
        self.assertTrue(mock_register_callback.called)


class RegisterMixinSendEmailConfirmationTestCase(TestCase):
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_it_sends_email_confirmation(self):
        request = RequestFactory().get(reverse('register'))
        RegisterMixin().send_email_confirmation(request, UserFactory())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, getattr(settings, 'EMAIL_CONFIRMATION_SUBJECT', None))


class RegisterMixinSendPhoneVerificationTestCase(TestCase):
    @patch('dj_accounts.authentication.verify_phone.VerifyPhone.send', autospec=True)
    def test_it_calls_send_phone_verification(self, mock_send):
        RegisterMixin().send_phone_verification(UserFactory())
        self.assertTrue(mock_send.called)


class RegisterGetFormClassMixinTestCase(TestCase):

    def test_it_returns_django_user_creation_form_if_settings_register_from_is_not_set(
            self):
        self.assertTrue(issubclass(RegisterMixin().get_form_class(), UserCreationForm))

    @override_settings(REGISTER_FORM='dj_accounts.authentication.forms.RegisterForm')
    def test_it_returns_settings_register_form_if_is_set(self):
        self.assertEquals(RegisterMixin().get_form_class(), RegisterForm)
