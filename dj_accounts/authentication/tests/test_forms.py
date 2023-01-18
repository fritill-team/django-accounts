from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory
from django.test import override_settings
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from .factories import UserFactory
from ..forms import MultipleLoginForm, RegisterForm, VerifyPhoneForm
from ..templatetags.auth import get_authentication_field_placeholder

UserModel = get_user_model()


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


def check_required(cls, key):
    data = {**cls.DEFAULT_DATA}
    data.pop(key, None)
    instance = cls.Form(data=data)
    cls.assertFalse(instance.is_valid())
    cls.assertEquals(instance.errors.as_data()[key][0].code, 'required')


def check_unique(cls, key, value):
    data = {**cls.DEFAULT_DATA}
    data.update({key: value})
    instance = cls.Form(data=data)
    cls.assertFalse(instance.is_valid())
    cls.assertEquals(instance.errors.as_data()[key][0].code, 'unique')


class RegistrationFormStructureTestCase(TestCase):
    def setUp(self):
        self.form = RegisterForm()

    def test_it_extends_django_Form(self):
        self.assertTrue(issubclass(RegisterForm, UserCreationForm))

    def test_it_has_email_field(self):
        self.assertIn('email', self.form.fields)

    def test_email_field_is_instance_of_email_field(self):
        self.assertIsInstance(self.form.fields['email'], forms.CharField)

    def test_email_field_max_length_is_100(self):
        self.assertEquals(self.form.fields['email'].max_length, 100)

    def test_email_field_help_text(self):
        self.assertEquals(self.form.fields['username'].help_text, _("Required, please provide your username"))

    def test_it_has_username_field(self):
        self.assertIn('username', self.form.fields)

    def test_username_field_is_instance_of_char_field(self):
        self.assertIsInstance(self.form.fields['username'], forms.CharField)

    def test_user_name_field_is_required(self):
        self.assertTrue(self.form.fields['username'].required)

    def test_username_field_max_length_is_100(self):
        self.assertEquals(self.form.fields['username'].max_length, 100)

    def test_username_field_help_text(self):
        self.assertEquals(self.form.fields['username'].help_text, _("Required, please provide your username"))

    def test_it_has_phone_field(self):
        self.assertIn('phone', self.form.fields)

    def test_phone_field_is_instance_of_char_field(self):
        self.assertIsInstance(self.form.fields['phone'], forms.CharField)

    def test_phone_field_is_required(self):
        self.assertTrue(self.form.fields['phone'].required)

    def test_phone_field_max_length_is_100(self):
        self.assertEquals(self.form.fields['phone'].max_length, 100)

    def test_phone_field_help_text(self):
        self.assertEquals(self.form.fields['phone'].help_text, _("Required, please provide your phone number"))


class RegisterFormValidationTest(TestCase):
    def setUp(self):
        self.DEFAULT_DATA = get_default_user_data()
        self.Form = RegisterForm
        UserModel.objects.create_user(
            email='first@aol.com', username="First User", first_name="First",
            last_name="User", phone="+201005263987")

    def test_username_is_required(self):
        check_required(self, 'username')

    def test_phone_is_required(self):
        check_required(self, 'phone')

    def test_phone_is_unique(self):
        check_unique(self, "phone", "+201005263987")

    def test_email_is_required(self):
        check_required(self, 'email')

    def test_email_is_unique(self):
        check_unique(self, "email", "first@aol.com")

    def test_password1_is_required(self):
        check_required(self, 'password1')

    def test_password2_is_required(self):
        check_required(self, 'password2')

    def test_password2_mismatch(self):
        data = self.DEFAULT_DATA
        data.update({
            "password1": "123654789",
            "password2": "123456789"
        })
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(form.errors.as_data()["password2"][0].code, 'password_mismatch')


class MultipleLoginFormStructureTestCase(TestCase):
    def setUp(self):
        self.request = RequestFactory()
        self.form = MultipleLoginForm(request=self.request)

    def test_it_extends_django_model_form(self):
        self.assertTrue(issubclass(MultipleLoginForm, forms.ModelForm))

    def test_it_has_cached_user(self):
        self.assertTrue(hasattr(self.form, 'user_cache'))

    def test_it_has_get_user_method(self):
        self.assertTrue(hasattr(self.form, 'get_user') and callable(self.form.get_user))

    def test_get_user_method_returns_cache_user_value(self):
        self.assertEquals(self.form.user_cache, self.form.get_user())

    def test_it_has_password_field(self):
        self.assertIn('password', self.form.fields)

    def test_password_field_is_instance_of_char_field(self):
        self.assertIsInstance(self.form.fields['password'], forms.CharField)

    def test_password_has_label_Password(self):
        self.assertEquals(self.form.fields['password'].label, _('Password'))

    def test_it_has_identifier_field(self):
        self.assertIn('identifier', self.form.fields)

    def test_identifier_field_is_instance_of_char_field(self):
        self.assertIsInstance(self.form.fields['identifier'], forms.CharField)

    def test_identifier_has_placeholder_of_user_model_authentication_fields(self):
        placeholder = get_authentication_field_placeholder()
        self.assertEquals(self.form.fields['identifier'].widget.attrs['placeholder'], placeholder)

    def test_password_field_not_striping_its_value(self):
        form = MultipleLoginForm()
        self.assertFalse(self.form.fields['password'].strip)

    def test_password_widget_is_instance_of_passwordInput(self):
        self.assertIsInstance(self.form.fields['password'].widget, forms.PasswordInput)

    def test_it_has_remember_me_field(self):
        self.assertIn('remember_me', self.form.fields)

    def test_remember_me_field_is_instance_of_charfield(self):
        self.assertIsInstance(self.form.fields['remember_me'], forms.BooleanField)

    def test_remember_me_field_has_label_Remember_Me(self):
        self.assertEquals(self.form.fields['remember_me'].label, _('Remember Me'))

    def test_remember_me_initial_value_is_false(self):
        self.assertEquals(self.form.fields['remember_me'].initial, False)


class MultipleLoginFormValidationTestCase(TestCase):
    @override_settings(AUTHENTICATION_BACKENDS=["dj_accounts.authentication.backends.MultipleAuthenticationBackend"])
    def setUp(self):
        self.request = RequestFactory().get('/')
        middleware = SessionMiddleware()
        middleware.process_request(self.request)
        self.request.session.save()
        self.user = UserFactory()
        self.Form = MultipleLoginForm
        self.user.phone = "01102158610"
        self.user.save()

    def test_it_fails_if_identifier_is_not_provided(self):
        form = self.Form(request=self.request, data={"password": "secret"})
        self.assertFalse(form.is_valid())
        self.assertEquals('required', form.errors.as_data()['identifier'][0].code)
        self.assertEquals(_("This field is required."), form.errors.as_data()['identifier'][0].message)

    def test_it_fails_if_password_is_not_provided(self):
        form = self.Form(request=self.request, data={
            "identifier": self.user.email
        })
        self.assertFalse(form.is_valid())
        self.assertEquals('required', form.errors.as_data()['password'][0].code)
        self.assertEquals(_("This field is required."), form.errors.as_data()['password'][0].message)

    def test_it_fails_if_credentials_are_not_provided(self):
        form = self.Form(request=self.request, data={})
        self.assertFalse(form.is_valid())
        self.assertEquals('required', form.errors.as_data()['identifier'][0].code)
        self.assertEquals(_("This field is required."), form.errors.as_data()['identifier'][0].message)
        self.assertEquals('required', form.errors.as_data()['password'][0].code)
        self.assertEquals(_("This field is required."), form.errors.as_data()['password'][0].message)

    def test_it_fails_if_password_is_not_correct(self):
        form = self.Form(request=self.request, data={
            "identifier": self.user.email,
            "password": "not a correct password"
        })
        self.assertFalse(form.is_valid())
        self.assertEquals('invalid_login', form.errors.as_data()['__all__'][0].code)
        self.assertEquals(_(
            "Please enter a correct credentials. Note that "
            "fields may be case-sensitive."
        ), form.errors.as_data()['__all__'][0].message)

    def test_it_fails_if_identifier_is_not_correct(self):
        form = self.Form(request=self.request, data={
            "identifier": "doesnotexist@mail.com",
            "password": "password"
        })
        self.assertFalse(form.is_valid())
        self.assertEquals('invalid_login', form.errors.as_data()['__all__'][0].code)
        self.assertEquals(_(
            "Please enter a correct credentials. Note that "
            "fields may be case-sensitive."
        ), form.errors.as_data()['__all__'][0].message)

    def test_it_saves_authenticated_user_in_user_cache(self):
        form = self.Form(request=self.request, data={
            "identifier": self.user.email,
            "password": "secret"
        })
        form.is_valid()
        self.assertEquals(form.user_cache, self.user)

    def test_get_user_method_returns_authenticated_user(self):
        form = self.Form(request=self.request, data={
            "identifier": self.user.email,
            "password": "secret"
        })
        form.is_valid()
        self.assertEquals(form.get_user(), self.user)

    def test_it_sets_session_expiry_to_zero_if_remember_me_is_false(self):
        form = self.Form(request=self.request, data={
            "identifier": self.user.email,
            "password": "secret",
            "remember_me": False
        })
        self.assertTrue(form.is_valid())
        self.assertIn('_session_expiry', self.request.session)
        self.assertEquals(0, self.request.session['_session_expiry'])


class VerifyPhoneFormTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory(phone="201002536987")
        self.form = VerifyPhoneForm(user=self.user)

    def test_it_extends_django_Form(self):
        self.assertIsInstance(self.form, forms.Form)

    def test_it_has_code_field(self):
        self.assertIn('code', self.form.fields)

    def test_code_label_is_correct(self):
        self.assertEquals(self.form.fields['code'].label, _("message sent to phone number: {}".format(self.user.phone)))

    def test_code_min_length_is_six_characters(self):
        self.assertEquals(self.form.fields['code'].min_length, 6)

    def test_code_max_length_is_six_characters(self):
        self.assertEquals(self.form.fields['code'].max_length, 6)


class VerifyPhoneFormValidationTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory(phone="201002536987")
        self.data = {"code": "777777"}

    @override_settings(PHONE_VERIFY_SERVICE="dj_accounts.authentication.tests.mocks.MockVerifyService")
    def test_it_fails_if_phone_verification_is_not_successful(self):
        self.data.update({"code": "888888"})
        form = VerifyPhoneForm(user=self.user, data=self.data)
        self.assertFalse(form.is_valid())
        self.assertEquals('invalid_code', form.errors.as_data()['__all__'][0].code)
        self.assertEquals(_("The Provided code is Properly invalid"), form.errors.as_data()['__all__'][0].message)

    @override_settings(PHONE_VERIFY_SERVICE="dj_accounts.authentication.tests.mocks.MockVerifyService")
    def test_it_passes_if_phone_verification_is_successful(self):
        form = VerifyPhoneForm(user=self.user, data=self.data)
        self.assertTrue(form.is_valid())
