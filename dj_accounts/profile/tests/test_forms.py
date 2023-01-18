from django import forms
from django.test import TestCase, RequestFactory
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from dj_accounts.authentication.tests.factories import UserFactory
from dj_accounts.profile.forms import UpdateEmailForm, UpdatePhoneNumberForm


def get_default_user_data():
    return {
        "email": "test@test.test",
        "username": "Test User",
        "phone": "+201005263988",
        "password1": "newTESTPasswordD",
        "password2": "newTESTPasswordD",
        "first_name": "Test",
        "last_name": "User",
        "gender": "male",
        "birthdate": now(),
    }


class UpdateUserDataFormStructureTestCase(TestCase):
    def setUp(self):
        self.form = UpdateUserDataForm()
        self.DEFAULT_DATA = get_default_user_data()

    def test_form_class_is_subclass_from_model_form(self):
        self.assertTrue(issubclass(UpdateUserDataForm, forms.ModelForm))

    def test_form_has_meta_class(self):
        self.assertTrue(hasattr(self.form, 'Meta'))

    def test_form_model_is_user_model(self):
        self.assertEquals(self.form.Meta.model, UserModel)

    def test_form_fields_are_equal_to_user_model_fields(self):
        self.assertEquals(self.form.Meta.fields, ('first_name', 'last_name'))

    def test_it_has_clean_first_name(self):
        self.assertTrue(hasattr(self.form, 'clean_first_name'))

    def test_it_has_clean_last_name(self):
        self.assertTrue(hasattr(self.form, 'clean_last_name'))

    def test_html_representation_has_first_name_field(self):
        self.assertIn('name="first_name"', str(self.form))

    def test_html_representation_has_last_name_field(self):
        self.assertIn('name="last_name"', str(self.form))


class UpdateUserFormValidationTest(TestCase):
    def setUp(self):
        self.DEFAULT_DATA = get_default_user_data()
        self.Form = UpdateUserDataForm

    def test_update_user_data_form(self):
        form = UpdateUserDataForm(data=self.DEFAULT_DATA)
        self.assertTrue(form.is_valid())

    def test_update_user_data_form_with_empty_first_name(self):
        check_required(self, 'first_name')

    def test_update_user_data_form_with_empty_last_name(self):
        check_required(self, 'last_name')

    def test_it_rais_error_message_if_no_first_name(self):
        self.DEFAULT_DATA.pop('first_name')
        form = UpdateUserDataForm(data=self.DEFAULT_DATA)
        self.assertFalse(form.is_valid())
        self.assertEquals(form.errors.as_data()['first_name'][0].code, 'required')

    def test_it_rais_error_message_if_no_last_name(self):
        self.DEFAULT_DATA.pop('last_name')
        form = UpdateUserDataForm(data=self.DEFAULT_DATA)
        self.assertFalse(form.is_valid())
        self.assertEquals(form.errors.as_data()['last_name'][0].code, 'required')

class UpdateEmailFormStructureTestCase(TestCase):
    def setUp(self):
        self.request = RequestFactory().get('/')
        self.user = UserFactory(email='test@test.test', password='secret')
        self.Form = UpdateEmailForm
        self.DEFAULT_DATA = {
            "new_email": 'new_test@test.test',
            "password": "secret",
        }

    def test_form_class_is_subclass_from_forms_form(self):
        self.assertTrue(issubclass(UpdateEmailForm, forms.Form))

    def test_html_representation_has_new_email_field(self):
        self.assertIn('name="new_email"', str(self.Form()))

    def test_html_representation_has_password_field(self):
        self.assertIn('name="password"', str(self.Form()))

    def test_form_has_error_messages_field(self):
        self.assertTrue(hasattr(self.Form, 'error_messages'))

    def test_it_has_clean_new_email(self):
        self.assertTrue(hasattr(self.Form, 'clean_new_email'))

    def test_it_has_clean_password(self):
        self.assertTrue(hasattr(self.Form, 'clean_password'))

    def test_it_has_save(self):
        self.assertTrue(hasattr(self.Form, 'save'))


class UpdateEmailFormValidationTest(TestCase):
    def setUp(self):
        self.request = RequestFactory().get('/')
        self.user = UserFactory(email='test@test.test', password='secret')
        self.Form = UpdateEmailForm
        self.DEFAULT_DATA = {
            "new_email": 'new_test@test.test',
            "password": "secret",
        }

    def test_email_form(self):
        form = UpdateEmailForm(data=self.DEFAULT_DATA, user=self.user)
        self.assertTrue(form.is_valid())

    def test_email_from_throw_error_if_provides_incomplete_data(self):
        form = UpdateEmailForm(data={}, user=self.user)
        self.assertFalse(form.is_valid())

    def test_email_from_throw_error_if_email_is_email_is_already_exists(self):
        default_data = {
            "new_email": 'test@test.test',
            "password": "secret",
        }
        form = UpdateEmailForm(data=default_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertEquals(form.errors.as_data()['new_email'][0].code, 'unique')

    def test_email_field_throw_error_if_old_email_equal_new_email(self):
        default_data = {
            "new_email": 'test@test.test',
            "password": "secret",
        }
        form = UpdateEmailForm(data=default_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertEquals(form.errors.as_data()['new_email'][0].code, 'unique')

    def test_email_from_throw_error_if_email_is_invalid(self):
        data = {
            "new_email": 'fake',
            "password": "secret",
        }
        form = UpdateEmailForm(data=data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['new_email'][0].code, 'invalid')

    def test_email_from_throw_error_if_password_is_invalid(self):
        data = {
            "new_email": 'test@test.sdfsd',
            'password': 'fake',
        }

        form = UpdateEmailForm(data=data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['password'][0].code, 'invalid')

    def test_ti_change_user_email(self):
        data = {
            "new_email": 'new@new.com',
            "password": "secret",
        }
        form = UpdateEmailForm(data=data, user=self.user)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(self.user.email, 'new@new.com')


class UpdatePhoneFormTestCase(TestCase):
    def setUp(self):
        self.request = RequestFactory()
        self.form = UpdatePhoneNumberForm()

    def test_it_extends_django_Form(self):
        self.assertIsInstance(UpdatePhoneNumberForm(), forms.Form)

    def test_it_has_phone_field(self):
        self.assertIn('new_phone', self.form.fields)

    def test_phone_field_is_instance_of_char_field(self):
        self.assertIsInstance(self.form.fields['new_phone'], forms.CharField)

    def test_phone_field_is_required(self):
        self.assertTrue(self.form.fields['new_phone'].required)

    def test_it_has_password_field(self):
        self.assertIn('password', self.form.fields)

    def test_password_field_is_instance_of_char_field(self):
        self.assertIsInstance(self.form.fields['password'], forms.CharField)

    def test_password_has_label_Password(self):
        self.assertEquals(self.form.fields['password'].label, _("Your Password"))

    def test_password_field_not_striping_its_value(self):
        form = UpdateEmailForm()
        self.assertFalse(self.form.fields['password'].strip)

    def test_password_widget_is_instance_of_passwordInput(self):
        self.assertIsInstance(self.form.fields['password'].widget, forms.PasswordInput)


class UpdatePhoneFormValidationTest(TestCase):
    def setUp(self):
        self.request = RequestFactory().get('/')
        self.user = UserFactory(phone="+201005263988")
        self.DEFAULT_DATA = get_default_user_data()
        self.Form = UpdatePhoneNumberForm
        self.DEFAULT_DATA = {
            "new_phone": '+201005263977',
            "password": "secret",
        }

    def test_phone_form(self):
        form = UpdatePhoneNumberForm(data=self.DEFAULT_DATA, user=self.user)
        self.assertTrue(form.is_valid())

    def test_phone_from_throw_error_if_provides_incomplete_data(self):
        form = UpdatePhoneNumberForm(data={}, user=self.user)
        self.assertFalse(form.is_valid())

    def test_phone_from_throw_error_if_new_phone_already_exists(self):
        default_data = {
            "new_phone": '+201005263988',
            "password": "secret",
        }
        form = UpdatePhoneNumberForm(data=default_data, user=self.user)
        self.assertFalse(form.is_valid())
