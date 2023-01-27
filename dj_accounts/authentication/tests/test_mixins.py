import inspect
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.core import mail
from django.test import TestCase, override_settings, RequestFactory
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from ..forms import MultipleLoginForm, RegisterForm, UserCreationForm, VerifyPhoneForm
from ..mixins import LoginGetFormClassMixin, RegisterMixin, SendEmailVerificationMixin, ViewCallbackMixin, \
    VerifyEmailMixin, SendPhoneVerificationMixin
from ..tests.factories import UserFactory
from ..tests.forms import TestLoginForm
from ...utils import account_activation_token


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
    def test_it_extends_SendEmailVerificationMixin_class(self):
        self.assertTrue(issubclass(RegisterMixin, SendEmailVerificationMixin))

    def test_it_extends_SendPhoneVerificationMixin_class(self):
        self.assertTrue(issubclass(RegisterMixin, SendPhoneVerificationMixin))

    def test_it_extends_ViewCallbackMixin_class(self):
        self.assertTrue(issubclass(RegisterMixin, ViewCallbackMixin))

    def test_it_has_get_form_class_method(self):
        self.assertIn('get_form_class', dict(inspect.getmembers(RegisterMixin)))

    def test_get_form_class_is_callable(self):
        self.assertTrue(callable(RegisterMixin.get_form_class))

    def test_get_form_class_method_signature(self):
        expected_signature = ['self']
        actual_signature = inspect.getfullargspec(RegisterMixin.get_form_class)[0]
        self.assertEquals(actual_signature, expected_signature)


class RegisterGetFormClassMixinTestCase(TestCase):

    def test_it_returns_django_user_creation_form_if_settings_register_from_is_not_set(
            self):
        self.assertTrue(issubclass(RegisterMixin().get_form_class(), UserCreationForm))

    @override_settings(REGISTER_FORM='dj_accounts.authentication.forms.RegisterForm')
    def test_it_returns_settings_register_form_if_is_set(self):
        self.assertEquals(RegisterMixin().get_form_class(), RegisterForm)


class SendEmailVerificationMixinTestCase(TestCase):
    def test_it_has_send_email_verification_method(self):
        self.assertIn('send_email_verification', dict(inspect.getmembers(SendEmailVerificationMixin)))

    def test_send_email_verification_is_callable(self):
        self.assertTrue(callable(SendEmailVerificationMixin.send_email_verification))

    def test_send_email_verification_method_signature(self):
        expected_signature = ['self', 'request', 'user']
        actual_signature = inspect.getfullargspec(SendEmailVerificationMixin.send_email_verification)[0]
        self.assertEquals(actual_signature, expected_signature)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_it_sends_email_verification(self):
        request = RequestFactory().get('/')
        SendEmailVerificationMixin().send_email_verification(request, UserFactory())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, getattr(settings, 'EMAIL_CONFIRMATION_SUBJECT', None))


class ViewCallbackMixinTestCase(TestCase):
    def test_it_has_get_callback_method(self):
        self.assertIn('get_callback', dict(inspect.getmembers(ViewCallbackMixin)))

    def test_get_callback_is_callable(self):
        self.assertTrue(callable(ViewCallbackMixin.get_callback))

    def test_get_callback_method_signature(self):
        expected_signature = ['self', 'key', 'user']
        actual_signature = inspect.getfullargspec(ViewCallbackMixin.get_callback)[0]
        self.assertEquals(actual_signature, expected_signature)

    @override_settings(REGISTER_CALLBACK='dj_accounts.authentication.tests.mocks.register_callback')
    @patch('dj_accounts.authentication.tests.mocks.register_callback', autospec=True)
    def test_it_calls_settings_register_callback_if_is_set(self, mock_get_callback):
        ViewCallbackMixin().get_callback('REGISTER_CALLBACK', UserFactory())
        self.assertTrue(mock_get_callback.called)


class VerifyEmailMixinTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = account_activation_token.make_token(self.user)

    def test_it_has_verify_method(self):
        self.assertIn('verify', dict(inspect.getmembers(VerifyEmailMixin)))

    def test_verify_is_callable(self):
        self.assertTrue(callable(VerifyEmailMixin.verify))

    def test_verify_method_signature(self):
        expected_signature = ['self', 'uidb64', 'token']
        actual_signature = inspect.getfullargspec(VerifyEmailMixin.verify)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_it_verifies_user_if_exists(self):
        VerifyEmailMixin().verify(self.uid, self.token)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.email_verified_at)

    def test_it_returns_user_and_success_status_of_verification(self):
        success, user = VerifyEmailMixin().verify(self.uid, self.token)
        self.assertTrue(success)
        self.assertEquals(user, self.user)

    def test_it_is_not_verifying_user_if_token_or_uid_is_not_valid(self):
        VerifyEmailMixin().verify('not-valid', self.token)
        self.assertIsNone(self.user.email_verified_at)

        VerifyEmailMixin().verify(self.uid, 'not-valid')
        self.assertIsNone(self.user.email_verified_at)


class SendPhoneVerificationMixinTestCase(TestCase):
    def test_it_has_send_phone_verification_method(self):
        self.assertIn('send_phone_verification', dict(inspect.getmembers(SendPhoneVerificationMixin)))

    def test_send_phone_verification_is_callable(self):
        self.assertTrue(callable(SendPhoneVerificationMixin.send_phone_verification))

    def test_send_phone_verification_method_signature(self):
        expected_signature = ['self', 'user']
        actual_signature = inspect.getfullargspec(SendPhoneVerificationMixin.send_phone_verification)[0]
        self.assertEquals(actual_signature, expected_signature)

    @patch('dj_accounts.authentication.verify_phone.VerifyPhone.send', autospec=True)
    def test_it_calls_send_phone_verification(self, mock_send):
        RegisterMixin().send_phone_verification(UserFactory())
        self.assertTrue(mock_send.called)


