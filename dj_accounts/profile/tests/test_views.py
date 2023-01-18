import inspect

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View

from dj_accounts.authentication.forms import RegisterForm
from dj_accounts.authentication.tests.factories import UserFactory
from dj_accounts.profile.forms import UpdateUserDataForm
from dj_accounts.profile.views import UpdateProfileView, ChangePhoneView


class UpdateProfileInfoViewStructureTestCase(TestCase):

    @override_settings(PROFILE_FORM=RegisterForm)
    def setUp(self):
        pass

    def test_it_extends_django_view_class(self):
        self.assertTrue(issubclass(UpdateProfileView, View))

    def test_it_extends_login_required_mixin(self):
        self.assertTrue(issubclass(UpdateProfileView, LoginRequiredMixin))

    def test_view_has_method_get_form_class(self):
        self.assertTrue(hasattr(UpdateProfileView, 'get_form_class'))

    def test_view_has_method_get(self):
        self.assertTrue(hasattr(UpdateProfileView, 'get'))

    def test_view_has_method_get_is_callable(self):
        self.assertTrue(callable(UpdateProfileView.get))

    def test_get_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(UpdateProfileView.get)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_view_has_method_post(self):
        self.assertTrue(hasattr(UpdateProfileView, 'post'))

    def test_view_has_method_post_is_callable(self):
        self.assertTrue(callable(UpdateProfileView.post))

    def test_post_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(UpdateProfileView.post)[0]
        self.assertEquals(actual_signature, expected_signature)


class UpdateProfileInfoGetViewTestCase(TestCase):

    @override_settings(PROFILE_FORM=UpdateUserDataForm)
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.client.login(username=self.user.username, password='secret')
        self.url = reverse('update-profile')

    def test_it_redirects_to_login_if_user_is_not_authenticated(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('login') + '?next=' + self.url)

    def test_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "dj_accounts/update_user_data_form.html")

    def test_context_contains_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_context_contains_page_title(self):
        response = self.client.get(self.url)
        self.assertIn("page_title", response.context)

    def test_context_page_title_is_instance_of_Update_form(self):
        response = self.client.get(self.url)
        self.assertEquals(response.context['page_title'], _("Update User Info"))


class UpdateProfileInfoPostViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = UserFactory(first_name='abc', last_name='xyz')
        self.client.login(email=self.user.email, password='secret')
        self.url = reverse('update-profile')
        self.data = {
            "first_name": "Test",
            "last_name": "User",
            'email': 'test@test.com',
        }

    def test_it_redirects_to_login_if_user_is_not_authenticated(self):
        self.client.logout()
        response = self.client.post(self.url, data=self.data)
        self.assertRedirects(response, reverse('login') + '?next=' + self.url)

    def test_template_used(self):
        response = self.client.post(self.url)
        self.assertTemplateUsed(response, "dj_accounts/update_user_data_form.html")

    def test_context_contains_form_on_error(self):
        response = self.client.post(self.url, data={})
        self.assertIn("form", response.context)

    @override_settings(PROFILE_FORM=UpdateUserDataForm)
    def test_it_redirect_to_success_url(self):
        response = self.client.post(self.url, data=self.data)
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False)

    @override_settings(PROFILE_FORM=UpdateUserDataForm)
    def test_message_value_when_data_posted_successfully(self):
        response = self.client.post(self.url, data=self.data)
        msgs = list(messages.get_messages(response.wsgi_request))
        self.assertEquals(str(msgs[0]), _('your profile has been updated successfully'))


class ChangeEmailViewGetTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory(username='test', password='secret')
        self.client.login(username=self.user.username, password='secret')
        self.url = reverse('change-email')

    def test_it_redirects_to_login_if_user_is_not_authenticated(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('login') + '?next=' + self.url, fetch_redirect_response=False)

    def test_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "dj_accounts/update_email_form.html")

    def test_context_contains_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_context_contains_page_title(self):
        response = self.client.get(self.url)
        print(response.context)

        self.assertIn("page_title", response.context)

    def test_context_page_title_is_instance_of_Update_form(self):
        response = self.client.get(self.url)
        self.assertEquals(response.context['page_title'], _("Update Email"))


class ChangeEmailViewPostTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory(username='test@test.test', password='secret')
        self.client.login(username=self.user.username, password='secret')
        self.url = reverse('change-email')
        self.data = {
            "new_email": 'test101@test.test',
            "password": "secret",
        }

    def test_it_redirects_to_login_if_user_is_not_authenticated(self):
        self.client.logout()
        response = self.client.post(self.url, data=self.data)
        self.assertRedirects(response, reverse('login') + '?next=' + self.url)

    def test_template_used(self):
        response = self.client.post(self.url)
        self.assertTemplateUsed(response, "dj_accounts/update_email_form.html")

    def test_context_contains_form(self):
        response = self.client.post(self.url)
        self.assertIn("form", response.context)

    def test_it_redirect_to_success_url(self):
        response = self.client.post(self.url, data=self.data)
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False)


class ChangePhoneViewGETTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory(phone="+201005263988")
        self.client.login(username=self.user.username, password='secret')
        self.url = reverse('change-phone')

    def test_it_redirects_to_login_if_user_is_not_authenticated(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('login') + '?next=' + self.url)

    def test_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "dj_accounts/update_phone_number_form.html")

    def test_context_contains_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_context_contains_page_title(self):
        response = self.client.get(self.url)
        self.assertIn("page_title", response.context)

    def test_context_page_title_is_instance_of_Update_form(self):
        response = self.client.get(self.url)
        self.assertEquals(response.context['page_title'], _("Update Phone Number"))


class ChangePhoneViewTestCase(TestCase):
    def test_it_extends_django_class_base_view(self):
        self.assertTrue(issubclass(ChangePhoneView, View))

    def test_it_extends_django_login_required_mixin(self):
        self.assertTrue(issubclass(ChangePhoneView, LoginRequiredMixin))

    def test_it_has_get_attribute(self):
        self.assertTrue(hasattr(ChangePhoneView, 'get'))

    def test_it_has_post_attribute(self):
        self.assertTrue(hasattr(ChangePhoneView, 'post'))

    def test_get_attribute_is_callable(self):
        self.assertTrue(callable(ChangePhoneView.get))

    def test_post_attribute_is_callable(self):
        self.assertTrue(callable(ChangePhoneView.post))

    def test_get_signature(self):
        expected_signature = ['self', 'request', ]
        actual_signature = inspect.getfullargspec(ChangePhoneView.get)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_post_signature(self):
        expected_signature = ['self', 'request', ]
        actual_signature = inspect.getfullargspec(ChangePhoneView.post)[0]
        self.assertEquals(actual_signature, expected_signature)


class ChangePhoneViewPOSTTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory(phone="+201001452369")
        self.client.login(username=self.user.username, password='secret')
        self.url = reverse('change-phone')
        self.data = {
            "new_phone": '+201005263977',
            "password": "secret",
        }

    def test_it_redirects_to_login_if_user_is_not_authenticated(self):
        self.client.logout()
        response = self.client.post(self.url, data=self.data)
        self.assertRedirects(response, reverse('login') + '?next=' + self.url)

    def test_template_used(self):
        response = self.client.post(self.url)
        self.assertTemplateUsed(response, "dj_accounts/update_phone_number_form.html")

    def test_context_contains_form(self):
        response = self.client.post(self.url)
        self.assertIn("form", response.context)

    def test_it_rerender_form_on_failure(self):
        UserFactory(phone='+201005263977')
        response = self.client.post(self.url, self.data)
        self.assertTemplateUsed(response, "dj_accounts/update_phone_number_form.html")

    def test_it_redirect_to_success_url(self):
        response = self.client.post(self.url, data=self.data)
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False)
