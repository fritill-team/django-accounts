import inspect

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.views import View

from .factories import UserFactory
from ..views import VerifyPhoneView, PhoneVerificationCompleteView, VerifyEmailView, \
    EmailVerificationCompleteView, ResendEmailVerificationLinkView, ResendPhoneVerificationView
from ...utils import account_activation_token

UserModel = get_user_model()


# phone views
class VerifyPhoneViewStructureTestCase(TestCase):
    def test_it_extends_django_view_class(self):
        self.assertTrue(issubclass(VerifyPhoneView, View))

    def test_it_extends_login_required_mixin(self):
        self.assertTrue(issubclass(VerifyPhoneView, LoginRequiredMixin))

    def test_view_has_method_get(self):
        self.assertTrue(hasattr(VerifyPhoneView, 'get'))

    def test_view_has_method_get_is_callable(self):
        self.assertTrue(callable(VerifyPhoneView.get))

    def test_get_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(VerifyPhoneView.get)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_view_has_method_post(self):
        self.assertTrue(hasattr(VerifyPhoneView, 'post'))

    def test_view_has_method_post_is_callable(self):
        self.assertTrue(callable(VerifyPhoneView.post))

    def test_post_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(VerifyPhoneView.post)[0]
        self.assertEquals(actual_signature, expected_signature)


class VerifyPhoneViewGETTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.client.login(email=self.user.email, password="secret")
        self.url = reverse('verify-phone')

    def test_it_redirects_to_login_if_user_is_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("login") + "?next=" + self.url, fetch_redirect_response=False)

    def test_it_redirects_to_settings_login_redirect_url_if_phone_is_verified(self):
        user = UserFactory(phone_verified_at=now())
        self.client.login(email=user.email, password="secret")
        response = self.client.get(self.url)
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False)

    def test_it_returns_verify_phone_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "dj_accounts/verify_phone.html")

    def test_it_returns_form_in_response_context(self):
        response = self.client.get(self.url)
        self.assertIn('form', response.context)


class VerifyPhoneViewPOSTTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory(phone="201002536987")
        self.client.login(email=self.user.email, password="secret")
        self.url = reverse('verify-phone')
        self.data = {"code": "777777"}

    def test_it_redirects_to_login_if_user_is_not_logged_in(self):
        self.client.logout()
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("login") + "?next=" + self.url, fetch_redirect_response=False)

    def test_it_redirects_to_settings_login_redirect_url_if_phone_is_verified(self):
        user = UserFactory(phone_verified_at=now())
        self.client.login(email=user.email, password="secret")
        response = self.client.post(self.url)
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False)

    def test_it_updates_phone_verified_at_column_in_user_model_to_now_on_success(self):
        self.client.post(self.url, self.data)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.phone_verified_at)

    def test_it_redirects_to_phone_verification_complete_on_success(self):
        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, reverse("phone-verification-complete"), fetch_redirect_response=False)

    def test_it_returns_verify_phone_template_on_failure(self):
        response = self.client.post(self.url)
        self.assertTemplateUsed(response, "dj_accounts/verify_phone.html")

    def test_it_returns_form_in_response_context_on_failure(self):
        response = self.client.post(self.url)
        self.assertIn('form', response.context)


class PhoneVerificationCompleteViewStructureTestCase(TestCase):
    def test_it_extends_django_view_class(self):
        self.assertTrue(issubclass(PhoneVerificationCompleteView, View))

    def test_it_extends_login_required_mixin(self):
        self.assertTrue(issubclass(PhoneVerificationCompleteView, LoginRequiredMixin))

    def test_view_has_method_get(self):
        self.assertTrue(hasattr(PhoneVerificationCompleteView, 'get'))

    def test_view_has_method_get_is_callable(self):
        self.assertTrue(callable(PhoneVerificationCompleteView.get))

    def test_get_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(PhoneVerificationCompleteView.get)[0]
        self.assertEquals(actual_signature, expected_signature)


class PhoneVerificationCompleteViewGETTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.client.login(email=self.user.email, password="secret")
        self.url = reverse('phone-verification-complete')

    def test_it_redirects_to_login_if_user_is_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("login") + "?next=" + self.url)

    def test_it_returns_phone_verification_complete_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "dj_accounts/phone_verification_complete.html")


class ResendPhoneVerificationViewStructureTestCase(TestCase):
    def test_it_extends_django_view_class(self):
        self.assertTrue(issubclass(ResendPhoneVerificationView, View))

    def test_it_extends_login_required_mixin(self):
        self.assertTrue(issubclass(ResendPhoneVerificationView, LoginRequiredMixin))

    def test_view_has_method_get(self):
        self.assertTrue(hasattr(ResendPhoneVerificationView, 'get'))

    def test_view_has_method_get_is_callable(self):
        self.assertTrue(callable(ResendPhoneVerificationView.get))

    def test_get_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(ResendPhoneVerificationView.get)[0]
        self.assertEquals(actual_signature, expected_signature)


class ResendPhoneVerificationViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.client.login(email=self.user.email, password="secret")
        self.url = reverse("resend_phone_activation")

    def test_it_redirects_to_login_if_user_is_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("login") + "?next=" + self.url)

    def test_it_redirect_to_phone_verification_again(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("verify-phone"))

    def test_message_is_correct(self):
        response = self.client.get(self.url, follow=True)
        msgs = list(messages.get_messages(response.wsgi_request))
        self.assertEquals(str(msgs[0]), _("A new verification code has been sent to your phone"))


# Email Verification


class VerifyEmailViewStructureTestCase(TestCase):

    def test_it_extends_login_required_mixin(self):
        self.assertTrue(issubclass(VerifyEmailView, LoginRequiredMixin))

    def test_it_extends_django_view_class(self):
        self.assertTrue(issubclass(VerifyEmailView, View))

    def test_view_has_method_get(self):
        self.assertTrue(hasattr(VerifyEmailView, 'get'))

    def test_view_has_method_get_is_callable(self):
        self.assertTrue(callable(VerifyEmailView.get))

    def test_get_method_signature(self):
        expected_signature = ['self', 'request', 'uidb64', 'token']
        actual_signature = inspect.getfullargspec(VerifyEmailView.get)[0]
        self.assertEquals(actual_signature, expected_signature)


class VerifyEmailViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.client.login(email=self.user.email, password="secret")
        self.user = UserFactory()
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = account_activation_token.make_token(self.user)

    def test_it_activate_the_user(self):
        confirm = self.client.get(reverse('verify-email', args=[self.uid, self.token]))
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.email_verified_at)

    def test_it_redirects_to_phone_verification_complete_on_success(self):
        confirm = self.client.get(reverse('verify-email', args=[self.uid, self.token]))
        self.assertRedirects(confirm, reverse('email-verification-complete'))





