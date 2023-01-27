from django.contrib.auth import views
from django.test import TestCase
from django.urls import resolve, reverse

from ..views import ResendPhoneVerificationView, VerifyPhoneView, LoginView, \
    RegisterView, ResendEmailVerificationLinkView as EmailVerificationView
from ..views_admin import SiteView, SiteCreateOrUpdateView, SiteDeleteView
from ..views_api import VerifyPhoneAPIView, \
    ResendPhoneVerificationAPIView, VerifyEmailAPIView, ResendEmailVerificationLinkAPIView, ChangePasswordAPIView, \
    LoginAPIView


class SiteUrlsTestCase(TestCase):
    def test_login_url_resolves(self):
        url = reverse('login')
        self.assertEquals(resolve(url).func.view_class, LoginView)

    def test_register_url_resolves(self):
        url = reverse('register')
        self.assertEquals(resolve(url).func.view_class, RegisterView)

    def test_logout_url_resolves(self):
        url = reverse('logout')
        self.assertEquals(resolve(url).func.view_class, views.LogoutView)

    # phone urls
    def test_phone_verify_url_resolves(self):
        url = reverse("verify-phone")
        self.assertEquals(resolve(url).func.view_class, VerifyPhoneView)

    def test_resend_phone_verification_url_resolves(self):
        url = reverse("resend_phone_activation")
        self.assertEquals(resolve(url).func.view_class, ResendPhoneVerificationView)

    def test_resend_email_verification_link_url_resolves(self):
        url = reverse("resend-email-verification")
        self.assertEquals(resolve(url).func.view_class, EmailVerificationView)


class APIUrlsTestCase(TestCase):
    def test_api_login_url_resolves(self):
        url = reverse('api_login')
        self.assertEquals(resolve(url).func.view_class, LoginAPIView)

    # EMAIL
    def test_verify_email_verification_url_resolves(self):
        url = reverse('api_verify_email', args=['token', 'email'])
        self.assertEquals(resolve(url).func.view_class, VerifyEmailAPIView)

    def test_resend_email_verification_code_url_resolves(self):
        url = reverse('api_resend_email_verification')
        self.assertEqual(resolve(url).func.view_class, ResendEmailVerificationLinkAPIView)

    def test_phone_verify_url_resolves(self):
        url = reverse("verify_phone_api")
        self.assertEquals(resolve(url).func.view_class, VerifyPhoneAPIView)

    def test_resend_phone_activation_code_url_resolves(self):
        url = reverse('resend_phone_activation_api')
        self.assertEqual(resolve(url).func.view_class, ResendPhoneVerificationAPIView)

    # profile
    # def test_user_update_profile_info_api_view_url_resolves(self):
    #     url = reverse('update-profile-api')
    #     self.assertEqual(resolve(url).func.view_class, UpdateProfileAPIView)

    # def test_update_user_email_api_view_url_resolves(self):
    #     url = reverse('change-email-api')
    #     self.assertEqual(resolve(url).func.view_class, ChangeEmailAPIView)
    #
    # def test_update_user_phone_api_view_url_resolves(self):
    #     url = reverse('change-phone-api')
    #     self.assertEqual(resolve(url).func.view_class, ChangePhoneAPIView)

    # password
    def test_password_change_api_view_url_resolves(self):
        url = reverse('change_password_api')
        self.assertEqual(resolve(url).func.view_class, ChangePasswordAPIView)


class AdminUrlsTestCase(TestCase):
    def test_sites_view_url_resolves(self):
        url = reverse('sites-view')
        self.assertEqual(resolve(url).func.view_class, SiteView)

    def test_create_site_url_resolves(self):
        url = reverse('create-site')
        self.assertEqual(resolve(url).func.view_class, SiteCreateOrUpdateView)

    def test_edit_site_url_resolves(self):
        url = reverse('edit-site', args=[1])
        self.assertEqual(resolve(url).func.view_class, SiteCreateOrUpdateView)

    def test_delete_site_url_resolves(self):
        url = reverse('delete-site', args=[1])
        self.assertEqual(resolve(url).func.view_class, SiteDeleteView)
