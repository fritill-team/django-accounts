import inspect

import pyotp
from django.test import TestCase, override_settings

from dj_accounts.authentication.tests.factories import UserFactory
from ..verify_phone import BaseOTP, HOTP, TOTP, get_otp_class
from ...utils import get_settings_value


class BaseOTPStructureTestCase(TestCase):
    def test___init___signature(self):
        expected_signature = ['self', 'user']
        actual_signature = inspect.getfullargspec(BaseOTP.__init__)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_it_has_authenticate_method(self):
        self.assertTrue(hasattr(BaseOTP, 'authenticate'))

    def test_it_authenticate_method_is_callable(self):
        self.assertTrue(callable(BaseOTP.authenticate))

    def test_authenticate_method_signature(self):
        expected_signature = ['self', 'otp']
        actual_signature = inspect.getfullargspec(BaseOTP.authenticate)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_it_has_verify_method(self):
        self.assertTrue(hasattr(BaseOTP, 'verify'))

    def test_it_verify_method_is_callable(self):
        self.assertTrue(callable(BaseOTP.verify))

    def test_verify_method_signature(self):
        expected_signature = ['self', 'otp']
        actual_signature = inspect.getfullargspec(BaseOTP.verify)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_verify_method_is_abstract(self):
        with self.assertRaises(NotImplementedError):
            BaseOTP(UserFactory()).verify('123455')

    def test_it_has_initialize_method(self):
        self.assertTrue(hasattr(BaseOTP, 'initialize'))

    def test_it_initialize_method_is_callable(self):
        self.assertTrue(callable(BaseOTP.initialize))

    def test_initialize_method_signature(self):
        expected_signature = ['self']
        actual_signature = inspect.getfullargspec(BaseOTP.initialize)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_initialize_method_is_abstract(self):
        with self.assertRaises(NotImplementedError):
            BaseOTP(UserFactory()).initialize()

    def test_it_has_get_method(self):
        self.assertTrue(hasattr(BaseOTP, 'get'))

    def test_it_get_method_is_callable(self):
        self.assertTrue(callable(BaseOTP.get))

    def test_get_method_signature(self):
        expected_signature = ['self']
        actual_signature = inspect.getfullargspec(BaseOTP.get)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_get_method_is_abstract(self):
        with self.assertRaises(NotImplementedError):
            BaseOTP(UserFactory()).get()


class BaseOTPInitTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_it_sets_user_property_to_user_parameter(self):
        with self.assertRaises(NotImplementedError):
            self.assertEquals(BaseOTP(self.user).user, self.user)

    def test_it_sets_otp_property_to_none(self):
        with self.assertRaises(NotImplementedError):
            self.assertIsNone(BaseOTP(self.user).otp)

    # @patch('dj_accounts.authentication.verify_phone.BaseOTP.initialize')
    # def test_it_calls_initialize_method(self, mocked_initialize):
    #     with self.assertRaises(NotImplementedError):
    #         self.assertTrue(mocked_initialize.called)


class HOTPStructureTestCase(TestCase):
    def test_it_extends_BaseOTP_class(self):
        self.assertTrue(issubclass(HOTP, BaseOTP))


class HOTPInitializeTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.hotp = HOTP(self.user)

    def test_it_updates_otp_property(self):
        self.assertIsNotNone(self.hotp.otp)

    def test_it_sets_otp_property_to_instance_of_pyotp_hotp(self):
        self.assertIsInstance(self.hotp.otp, pyotp.HOTP)

    def test_otp_code_length(self):
        self.assertEquals(self.hotp.otp.digits, get_settings_value('PHONE_VERIFICATION_CODE_LENGTH', 6))


class HOTPVerifyTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.user.otp_counter = 0
        self.hotp = HOTP(self.user)

    def test_it_returns_true_if_otp_is_valid(self):
        self.assertTrue(self.hotp.verify(self.hotp.otp.at(0)))

    def test_it_returns_false_if_otp_is_invalid(self):
        self.assertFalse(self.hotp.verify(self.hotp.otp.at(1)))

    def test_it_updates_user_otp_counter_if_otp_is_valid(self):
        self.hotp.verify(self.hotp.otp.at(0))
        self.assertEqual(self.user.otp_counter, 1)

    def test_it_does_not_update_user_otp_counter_if_otp_is_invalid(self):
        self.hotp.verify(self.hotp.otp.at(1))
        self.assertEqual(self.user.otp_counter, 0)


class HOTPGetTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.user.otp_counter = 0
        self.hotp = HOTP(self.user)

    def test_it_returns_otp_at_current_otp_count(self):
        self.assertEquals(self.hotp.get(), self.hotp.otp.at(self.user.otp_counter))
        self.user.otp_counter += 1
        self.assertEquals(self.hotp.get(), self.hotp.otp.at(self.user.otp_counter))


class TOTPStructureTestCase(TestCase):
    def test_it_extends_BaseOTP_class(self):
        self.assertTrue(issubclass(TOTP, BaseOTP))


class TOTPInitializeTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.totp = TOTP(self.user)

    def test_it_updates_otp_property(self):
        self.assertIsNotNone(self.totp.otp)

    def test_otp_code_length(self):
        self.assertEquals(self.totp.otp.digits, get_settings_value('PHONE_VERIFICATION_CODE_LENGTH', 6))

    def test_otp_interval(self):
        self.assertEquals(self.totp.otp.interval, get_settings_value('PHONE_VERIFICATION_CODE_INTERVAL', 60))

    def test_it_sets_otp_property_to_instance_of_pyotp_totp(self):
        self.assertIsInstance(self.totp.otp, pyotp.TOTP)


class TOTPVerifyTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.totp = TOTP(self.user)

    def test_it_returns_true_if_otp_is_valid(self):
        self.assertTrue(self.totp.verify(self.totp.otp.now()))

    def test_it_returns_false_if_otp_is_invalid(self):
        self.assertFalse(self.totp.verify('1213185'))


class TOTPGetTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.totp = TOTP(self.user)

    def test_it_returns_otp_at_current_otp_now(self):
        self.assertEquals(self.totp.get(), self.totp.otp.now())


class GetOTPClassTestCase(TestCase):
    def test_it_returns_totp_class_by_default(self):
        self.assertEquals(get_otp_class(), TOTP)

    @override_settings(OTP_VERIFICATION_TYPE="HOTP")
    def test_it_returns_hotp_class_if_provided_in_settings(self):
        self.assertEquals(get_otp_class(), HOTP)

    @override_settings(OTP_VERIFICATION_TYPE="TOTP")
    def test_it_returns_hotp_class_if_provided_in_settings(self):
        self.assertEquals(get_otp_class(), TOTP)

    @override_settings(OTP_VERIFICATION_TYPE="Not-valid")
    def test_it_raises_key_Error_if_settings_key_is_invalid(self):

        with self.assertRaises(KeyError) as e:
            get_otp_class()
            self.assertEquals(e.exception, "OTP_VERIFICATION_TYPE is not valid, it must be HOTP or TOTP")

# class VerifyPhoneSendTestCase(TestCase):
#     def setUp(self):
#         self.phone = "201002536987"
#
#     @override_settings(PHONE_VERIFY_SERVICE="dj_accounts.authentication.tests.mocks.MockVerifyService")
#     def test_it_calls_the_select_service_send(self):
#         success = VerifyPhone().send(phone=self.phone)
#         self.assertTrue(success)
#
#
# class VerifyPhoneCheckTestCase(TestCase):
#     def setUp(self):
#         self.phone = "201002536987"
#         self.code = "777777"
#
#     @override_settings(PHONE_VERIFY_SERVICE="dj_accounts.authentication.tests.mocks.MockVerifyService")
#     def test_it_calls_the_selected_service_check(self):
#         success = VerifyPhone().check(phone=self.phone, code=self.code)
#         self.assertTrue(success)
#
#     @override_settings(PHONE_VERIFY_SERVICE="dj_accounts.authentication.tests.mocks.MockVerifyService")
#     def test_it_returns_false_if_phone_or_code_is_not_correct(self):
#         success = VerifyPhone().check(phone="201063598876", code=self.code)
#         self.assertFalse(success)
#
#
# class VerifyPhoneGetServiceClassTestCase(TestCase):
#     @override_settings(PHONE_VERIFY_SERVICE="dj_accounts.authentication.tests.mocks.MockVerifyService")
#     def test_it_returns_subclass_of_verify_phone_abstract(self):
#         class_ = VerifyPhone().get_service_class()
#         self.assertIsInstance(class_, BaseVerifyPhoneService)
