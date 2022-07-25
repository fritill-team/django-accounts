from ..views import ResendPhoneConfirmationView, VerifyPhoneView, PhoneVerificationCompleteView, LoginView, \
    RegisterView, ResendEmailConfirmationLinkView as EmailConfirmationView, ChangeEmailView, ChangePhoneView, \
    UpdateProfileView
from ..views_api import UpdateProfileAPIView, ChangeEmailAPIView, ChangePhoneAPIView, VerifyPhoneAPIView, \
    ResendPhoneConfirmationAPIView, VerifyEmailAPIView, ResendEmailConfirmationLinkAPIView, ChangePasswordAPIView
from django.contrib.auth import views
from django.test import TestCase
from django.urls import resolve, reverse


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

    def test_resend_phone_confirmation_url_resolves(self):
        url = reverse("resend_phone_activation")
        self.assertEquals(resolve(url).func.view_class, ResendPhoneConfirmationView)

    def test_phone_verify_complete_url_resolves(self):
        url = reverse("phone-verification-complete")
        self.assertEquals(resolve(url).func.view_class, PhoneVerificationCompleteView)

    # Email Verification
    def test_resend_email_confirmation_link_url_resolves(self):
        url = reverse("resend-email-confirmation")
        self.assertEquals(resolve(url).func.view_class, EmailConfirmationView)

    def test_change_email_url_resolves(self):
        url = reverse("change-email")
        self.assertEquals(resolve(url).func.view_class, ChangeEmailView)

    def test_change_phone_url_resolves(self):
        url = reverse("change-phone")
        self.assertEquals(resolve(url).func.view_class, ChangePhoneView)

    def test_update_profile_url_resolves(self):
        url = reverse("update-profile")
        self.assertEquals(resolve(url).func.view_class, UpdateProfileView)


class APIUrlsTestCase(TestCase):

    # EMAIL
    def test_verify_email_confirmation_url_resolves(self):
        url = reverse('verify_email_api', args=['token', 'email'])
        self.assertEquals(resolve(url).func.view_class, VerifyEmailAPIView)

    def test_resend_email_confirmation_code_url_resolves(self):
        url = reverse('resend_email_activation_api')
        self.assertEqual(resolve(url).func.view_class, ResendEmailConfirmationLinkAPIView)

    # phone verification
    def test_phone_verify_url_resolves(self):
        url = reverse("verify_phone_api")
        self.assertEquals(resolve(url).func.view_class, VerifyPhoneAPIView)

    def test_resend_phone_activation_code_url_resolves(self):
        url = reverse('resend_phone_activation_api')
        self.assertEqual(resolve(url).func.view_class, ResendPhoneConfirmationAPIView)

    # profile
    def test_user_update_profile_info_api_view_url_resolves(self):
        url = reverse('update-profile-api')
        self.assertEqual(resolve(url).func.view_class, UpdateProfileAPIView)

    def test_update_user_email_api_view_url_resolves(self):
        url = reverse('change-email-api')
        self.assertEqual(resolve(url).func.view_class, ChangeEmailAPIView)

    def test_update_user_phone_api_view_url_resolves(self):
        url = reverse('change-phone-api')
        self.assertEqual(resolve(url).func.view_class, ChangePhoneAPIView)

    # password
    def test_password_change_api_view_url_resolves(self):
        url = reverse('change_password_api')
        self.assertEqual(resolve(url).func.view_class, ChangePasswordAPIView)
