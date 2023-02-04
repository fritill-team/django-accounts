import inspect
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.core import mail
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, override_settings, RequestFactory
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.timezone import now

from .models import UserPhone
from ..forms import MultipleLoginForm, RegisterForm, UserCreationForm, VerifyPhoneForm
from ..mixins import LoginGetFormClassMixin, RegisterMixin, SendEmailVerificationMixin, ViewCallbackMixin, \
    VerifyEmailMixin, SendPhoneVerificationMixin, VerifyPhoneMixin
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


class VerifyPhoneMixinStructureTestCase(TestCase):
    def test_it_has_form_class_property(self):
        self.assertTrue(hasattr(VerifyPhoneMixin, 'form_class'))

    def test_form_class_is_VerifyPhoneForm(self):
        self.assertEquals(VerifyPhoneMixin.form_class, VerifyPhoneForm)

    def test_it_has_get_phone_method(self):
        self.assertTrue(hasattr(VerifyPhoneMixin, 'get_phone'))

    def test_it_get_phone_method_is_callable(self):
        self.assertTrue(callable(VerifyPhoneMixin.get_phone))

    def test_get_phone_method_signature(self):
        expected_signature = ['self']
        actual_signature = inspect.getfullargspec(VerifyPhoneMixin.get_phone)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_it_has_get_form_method(self):
        self.assertTrue(hasattr(VerifyPhoneMixin, 'get_form'))

    def test_it_get_form_method_is_callable(self):
        self.assertTrue(callable(VerifyPhoneMixin.get_form))

    def test_get_form_method_signature(self):
        expected_signature = ['self']
        actual_signature = inspect.getfullargspec(VerifyPhoneMixin.get_form)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_it_has_get_context_method(self):
        self.assertTrue(hasattr(VerifyPhoneMixin, 'get_context'))

    def test_it_get_context_method_is_callable(self):
        self.assertTrue(callable(VerifyPhoneMixin.get_context))

    def test_get_context_method_signature(self):
        expected_signature = ['self']
        actual_signature = inspect.getfullargspec(VerifyPhoneMixin.get_context)[0]
        self.assertEquals(actual_signature, expected_signature)


class VerifyPhoneMixinInitTestCase(TestCase):
    def setUp(self):
        self.mixin = VerifyPhoneMixin()

    def test_it_sets_phone_to_none(self):
        self.assertIsNone(self.mixin.phone)

    def test_it_sets_hashed_phone_to_none(self):
        self.assertIsNone(self.mixin.hashed_phone)

    def test_it_sets_form_to_none(self):
        self.assertIsNone(self.mixin.form)

    def test_it_sets_is_verified_to_false(self):
        self.assertFalse(self.mixin.is_verified)


class VerifyPhoneMixinGetPhoneTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.mixin = VerifyPhoneMixin()
        self.request = RequestFactory().get(reverse('verify-phone'))
        self.request.user = self.user
        self.mixin.request = self.request

    def test_it_sets_phone_to_request_user_phone(self):
        self.mixin.get_phone()
        self.assertEquals(self.mixin.phone, self.user.phone)

    def test_it_sets_hashed_phone_to_request_user_hashed_phone(self):
        self.mixin.get_phone()
        phone = str(self.user.phone)
        self.assertEquals(self.mixin.hashed_phone, ''.join(['*' for i in phone[4:-3]]).join([phone[:4], phone[-3:]]))

    def test_it_sets_is_verified_to_boolean_value_of_user_phone_verified_at(self):
        self.mixin.get_phone()
        self.assertFalse(self.mixin.is_verified)
        self.user.phone_verified_at = now()
        self.mixin.get_phone()
        self.assertTrue(self.mixin.is_verified)


class VerifyPhoneMixinGetPhoneWithMultiplePhonesTestCase(TestCase):
    """
    tests VerifyPhoneMixin.get_phone when USER_PHONE_MODEL is provided
    """

    def setUp(self):
        self.user = UserFactory()
        self.user_phone = UserPhone.objects.create(
            user=self.user, phone=self.user.phone
        )
        self.mixin = VerifyPhoneMixin()
        self.request = RequestFactory().get(reverse('verify-phone'))
        self.request.user = self.user
        self.mixin.request = self.request
        self.mixin.kwargs = {"phone_id": self.user_phone.pk}

    @override_settings(USER_PHONE_MODEL='dj_accounts.authentication.tests.models.UserPhone')
    def test_it_raises_ObjectDoesNotExist_if_phone_does_not_exist(self):
        with self.assertRaises(ObjectDoesNotExist) as e:
            self.mixin.kwargs = {"phone_id": 2}
            self.mixin.get_phone()
            self.assertEquals(e.exception, "Phone Not Found!")

    @override_settings(USER_PHONE_MODEL='dj_accounts.authentication.tests.models.UserPhone')
    def test_it_sets_phone_to_request_user_phone_provided_in_kwargs(self):
        self.mixin.get_phone()
        self.assertEquals(self.mixin.phone, self.user_phone.phone)

    @override_settings(USER_PHONE_MODEL='dj_accounts.authentication.tests.models.UserPhone')
    def test_it_sets_is_verified_to_boolean_value_of_user_phone_verified_at(self):
        self.mixin.get_phone()
        self.assertFalse(self.mixin.is_verified)
        self.user_phone.phone_verified_at = now()
        self.user_phone.save()

        self.mixin.get_phone()
        self.assertTrue(self.mixin.is_verified)

    @override_settings(USER_PHONE_MODEL='dj_accounts.authentication.tests.models.UserPhone')
    def test_it_sets_hashed_phone_to_request_user_hashed_phone(self):
        self.mixin.get_phone()
        phone = str(self.user_phone.phone)
        self.assertEquals(self.mixin.hashed_phone, ''.join(['*' for i in phone[4:-3]]).join([phone[:4], phone[-3:]]))


class VerifyPhoneMixinGetFormTestCase(TestCase):
    def test_it_sets_form_property_with_instance_of_from_class_property(self):
        mixin = VerifyPhoneMixin()
        mixin.request = RequestFactory().get(reverse('verify-phone'))
        mixin.request.user = UserFactory()
        mixin.get_form()
        self.assertIsInstance(mixin.form, mixin.form_class)


class VerifyPhoneMixinGetContextTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.mixin = VerifyPhoneMixin()
        self.mixin.request = RequestFactory().get(reverse('verify-phone'))
        self.mixin.request.user = self.user
        self.mixin.get_phone()
        self.mixin.get_form()

    def test_it_returns_dict(self):
        context = self.mixin.get_context()
        self.assertIsInstance(context, dict)

    def test_it_returns_hashed_phone(self):
        context = self.mixin.get_context()
        self.assertIn('hashed_phone', context)
        self.assertEquals(context['hashed_phone'], self.mixin.hashed_phone)

    def test_it_returns_otp_length(self):
        context = self.mixin.get_context()
        self.assertIn('otp_length', context)
        self.assertEquals(context['otp_length'], 6)

    def test_it_returns_otp_range(self):
        context = self.mixin.get_context()
        self.assertIn('otp_range', context)
        self.assertEquals(context['otp_range'], range(6))

    def test_it_returns_form(self):
        context = self.mixin.get_context()
        self.assertIn('form', context)
        self.assertEquals(context['form'], self.mixin.form)

    def test_it_returns_otp_expiry(self):
        context = self.mixin.get_context()
        self.assertIn('otp_expiry', context)

