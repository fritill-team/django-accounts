from django.test import TestCase
from django.test import override_settings
from django.test.client import RequestFactory
from django.utils.translation import gettext as _
from rest_framework import serializers

from ..serializers import LogoutSerializer, RegisterSerializer, UpdateUserDataSerializer, UpdateEmailSerializer, \
    UpdatePhoneNumberSerializer, ChangePasswordSerializer
from ..tests.factories import UserFactory


class RegistrationSerializerStructureTestCase(TestCase):
    def setUp(self):
        self.serializer = RegisterSerializer()

    def test_it_extends_drf_serializer(self):
        self.assertTrue(issubclass(RegisterSerializer, serializers.ModelSerializer))

    def test_it_has_get_form_class_method(self):
        self.assertTrue(hasattr(self.serializer, 'get_form_class'))

    def test_get_form_class_method_is_callable(self):
        self.assertTrue(callable(self.serializer.get_form_class))

    @override_settings(REGISTER_FORM='dj_accounts.forms.RegisterForm')
    def test_it_returns_instance_of_settings_register_form_if_register_form_is_set(self):
        from dj_accounts.forms import RegisterForm
        self.assertIs(self.serializer.get_form_class(), RegisterForm)

    def test_it_returns_use_creation_form_if_settings_register_form_is_not_set(self):
        from dj_accounts.forms import UserCreationForm
        self.assertIs(self.serializer.get_form_class(), UserCreationForm)

    # @override_settings(REGISTER_FORM='dj_accounts.forms.RegisterForm')
    # def test_serializer_meta_fields_is_equal_to_register_form_meta_fields(self):
    #     from dj_accounts.forms import RegisterForm
    #     print(self.serializer.Meta.fields)
    #     self.assertTupleEqual(self.serializer.Meta.fields, RegisterForm.Meta.fields)

    def test_serializer_meta_fields_is_equal_to_user_creation_form_meta_fields(self):
        from dj_accounts.forms import UserCreationForm
        self.assertTupleEqual(self.serializer.Meta.fields, UserCreationForm.Meta.fields)


class RegisterSerializerValidationTestCase(TestCase):
    def setUp(self):
        self.serializer = RegisterSerializer
        self.data = {
            'email': 'test@mail.com',
            'password1': "aa111111aa",
            'password2': "aa111111aa",
            "username": "Test User",
            "phone": "+380991234567"
        }

    def test_it_returns_validation_error_if_email_is_not_in_data(self):
        serializer = self.serializer(data=self.data)
        serializer.is_valid()


class LogoutSerializerStructureTestCase(TestCase):
    def setUp(self):
        self.serializer = LogoutSerializer(data={'refresh': 'test'})

    def test_it_has_refresh_field(self):
        self.assertIn('refresh', self.serializer.fields)

    def test_refresh_field_help_text(self):
        self.assertEquals(self.serializer.fields['refresh'].help_text, _("Required, please provide your refresh token"))

    def test_refresh_field_is_instance_of_char_field(self):
        self.assertIsInstance(self.serializer.fields['refresh'], serializers.CharField)

    def test_refresh_field_is_required(self):
        self.assertTrue(self.serializer.fields['refresh'].required)

    def test_it_has_save_method(self):
        self.assertTrue(hasattr(self.serializer, 'save'))


# profile serializer tests

class UpdateUserDataSerializerStructureTestCase(TestCase):
    def setUp(self):
        self.serializer = UpdateUserDataSerializer(data={})

    def test_it_has_meta_class(self):
        self.assertIsInstance(self.serializer.Meta, type)

    def test_it_has_model_class_in_meta(self):
        self.assertTrue(hasattr(self.serializer.Meta, 'model'))

    def test_it_has_fields_in_meta(self):
        self.assertTrue(hasattr(self.serializer.Meta, 'fields'))

    def test_it_has_first_name_field(self):
        self.assertIn('first_name', self.serializer.fields)

    def test_it_has_last_name_field(self):
        self.assertIn('last_name', self.serializer.fields)


class UpdateEmailSerializerStructureTestCase(TestCase):
    def setUp(self):
        self.serializer = UpdateEmailSerializer(data={})

    def test_it_has_meta_class(self):
        self.assertIsInstance(self.serializer.Meta, type)

    def test_it_has_model_class_in_meta(self):
        self.assertTrue(hasattr(self.serializer.Meta, 'model'))

    def test_it_has_fields_in_meta(self):
        self.assertTrue(hasattr(self.serializer.Meta, 'fields'))

    def test_it_has_email_field(self):
        self.assertIn('email', self.serializer.fields)

    def test_it_has_password_field(self):
        self.assertIn('password', self.serializer.fields)


class UpdatePhoneSerializerStructureTestCase(TestCase):
    def setUp(self):
        self.serializer = UpdatePhoneNumberSerializer(data={})

    def test_it_has_meta_class(self):
        self.assertIsInstance(self.serializer.Meta, type)

    def test_it_has_model_class_in_meta(self):
        self.assertTrue(hasattr(self.serializer.Meta, 'model'))

    def test_it_has_fields_in_meta(self):
        self.assertTrue(hasattr(self.serializer.Meta, 'fields'))

    def test_it_has_phone_field(self):
        self.assertIn('phone', self.serializer.fields)

    def test_it_has_password_field(self):
        self.assertIn('password', self.serializer.fields)


class ChangePasswordSerializerStructureTestCase(TestCase):
    def setUp(self):
        self.serializer = ChangePasswordSerializer()

    def test_it_has_model_class_in_meta(self):
        self.assertTrue(hasattr(self.serializer.Meta, 'model'))

    def test_it_has_fields_in_meta(self):
        self.assertTrue(hasattr(self.serializer.Meta, 'fields'))

    def test_it_has_new_password1_field(self):
        self.assertIn('new_password1', self.serializer.fields)

    def test_it_has_new_password2_field(self):
        self.assertIn('new_password2', self.serializer.fields)

    def test_it_has_old_password_field(self):
        self.assertIn('old_password', self.serializer.fields)

    def test_it_has_form_attribute(self):
        self.assertTrue(hasattr(self.serializer, 'form'))

    def test_it_has_method_validate(self):
        self.assertTrue(hasattr(self.serializer, 'validate'))

    def test_it_has_method_save(self):
        self.assertTrue(hasattr(self.serializer, 'save'))


class ChangePasswordSerializerTestCase(TestCase):
    def setUp(self):
        self.request = RequestFactory()
        self.user = UserFactory()
        self.request.user = self.user
        self.old_password = self.user.password
        self.data = {
            "new_password1": "12345678Aa",
            "new_password2": "12345678Aa",
            "old_password": "secret"
        }

    def test_it_change_password(self):
        serializer = ChangePasswordSerializer(data=self.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.user.refresh_from_db()
        self.assertNotEqual(self.old_password, self.user.password)
