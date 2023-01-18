import inspect

from django.conf import settings
from django.contrib.auth.views import LoginView as BaseLoginView
from django.test import TestCase, Client
from django.test import override_settings
from django.urls import reverse

from dj_accounts.authentication.mixins import LoginGetFormClassMixin
from dj_accounts.authentication.tests.factories import UserFactory
from dj_accounts.authentication.views import LoginView


class LoginViewStructureTestCase(TestCase):
    def test_it_extends_django_login_view(self):
        self.assertTrue(issubclass(LoginView, BaseLoginView))

    def test_it_extends_get_form_class_mixin(self):
        self.assertTrue(issubclass(LoginView, LoginGetFormClassMixin))

    def test_it_has_template_name(self):
        self.assertIn('template_name', dict(inspect.getmembers(LoginView)))

    def test_template_name_is_authentication_login(self):
        self.assertEquals(LoginView().get_template_names(), ['dj_accounts/authentication/themes/corporate/login.html'])

    def test_it_has_redirect_authenticated_user(self):
        self.assertIn('redirect_authenticated_user', dict(inspect.getmembers(LoginView)))

    def test_redirect_authenticated_user_is_true(self):
        self.assertTrue(LoginView.redirect_authenticated_user)


class LoginViewGetTemplateNamesTestCase(TestCase):
    @override_settings(AUTHENTICATION_THEME='creative')
    def test_it_returns_template_name_based_on_settings_authentication_theme_option(
            self):
        template_name = LoginView().get_template_names()
        self.assertEquals(['dj_accounts/authentication/themes/creative/login.html'], template_name)