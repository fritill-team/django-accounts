import inspect

from django.contrib.auth.forms import AuthenticationForm
from django.test import TestCase, override_settings

from dj_accounts.authentication.forms import MultipleLoginForm
from dj_accounts.authentication.mixins import LoginGetFormClassMixin
from dj_accounts.authentication.tests.forms import TestLoginForm


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
