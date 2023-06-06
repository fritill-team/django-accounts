from django.test import TestCase
from django.test.client import RequestFactory

from ..serializers import UpdateUserDataSerializer, UpdateEmailSerializer, \
    UpdatePhoneNumberSerializer, ChangePasswordSerializer
from ..tests.factories import UserFactory


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
