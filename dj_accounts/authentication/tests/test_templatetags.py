from django.test import TestCase, override_settings
from django.utils.translation import gettext_lazy as _

from ..templatetags.auth import get_authentication_field_placeholder


class GetAuthenticationFieldPlaceholderTestCase(TestCase):

    def test_it_returns_string_with_authentication_fields(self):
        result = get_authentication_field_placeholder()
        self.assertEquals(_("email, username, phone or ID"), result)

    @override_settings(AUTH_USER_MODEL='tests.VerboseNameFieldsUser')
    def test_it_returns_string_of_joined_verbose_names_of_authentication_fields_if_exists(self):
        result = get_authentication_field_placeholder()
        self.assertEquals(_("Email, username, Phone or ID"), result)

    @override_settings(AUTH_USER_MODEL='tests.NoAuthenticationFieldsUser')
    def test_it_raises_exception_if_model_not_implementing_authentication_fields_property(self):
        with self.assertRaises(Exception) as e:
            result = get_authentication_field_placeholder()
            self.assertEquals("User model must implement AUTHENTICATION_FIELDS list", e.message)
