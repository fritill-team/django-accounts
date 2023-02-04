import inspect
from unittest.mock import patch

import pyotp
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, override_settings
from django.utils.timezone import now
from django.utils.translation import gettext as _

from dj_accounts.authentication.tests.factories import UserFactory
from .mocks import MockVerifyService
from .models import UserPhone
from ..verify_phone import BaseOTP, HOTP, TOTP, get_otp_class, BaseVerifyPhoneService, VerifyPhone
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


class BaseVerifyPhoneServiceStructureTestCase(TestCase):
    def test___init___signature(self):
        expected_signature = ['self', 'user', 'phone']
        actual_signature = inspect.getfullargspec(BaseVerifyPhoneService.__init__)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_it_has_send_method(self):
        self.assertTrue(hasattr(BaseVerifyPhoneService, 'send'))

    def test_it_send_method_is_callable(self):
        self.assertTrue(callable(BaseVerifyPhoneService.send))

    def test_send_method_signature(self):
        expected_signature = ['self']
        actual_signature = inspect.getfullargspec(BaseVerifyPhoneService.send)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_send_method_is_abstract(self):
        with self.assertRaises(NotImplementedError):
            user = UserFactory()
            BaseVerifyPhoneService(user, user.phone).send()

    def test_it_has_check_method(self):
        self.assertTrue(hasattr(BaseVerifyPhoneService, 'check'))

    def test_it_check_method_is_callable(self):
        self.assertTrue(callable(BaseVerifyPhoneService.check))

    def test_check_method_signature(self):
        expected_signature = ['self', 'code']
        actual_signature = inspect.getfullargspec(BaseVerifyPhoneService.check)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_check_method_is_abstract(self):
        with self.assertRaises(NotImplementedError):
            user = UserFactory()
            BaseVerifyPhoneService(user, user.phone).check('000000')


class BaseVerifyPhoneServiceInitTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.service = BaseVerifyPhoneService(self.user, self.user.phone)

    def test_it_sets_user_to_user_parameter(self):
        self.assertEquals(self.user, self.service.user)

    def test_it_sets_phone_to_phone_parameter(self):
        self.assertEquals(self.user.phone, self.service.phone)

    def test_it_sets_otp_to_an_instance_of_otp_class_based_on_settings(self):
        self.assertIsInstance(self.service.otp, TOTP)


class VerifyPhoneStructureTestCase(TestCase):
    def test___init___signature(self):
        expected_signature = ['self', 'user', 'phone']
        actual_signature = inspect.getfullargspec(VerifyPhone.__init__)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_it_has_send_method(self):
        self.assertTrue(hasattr(VerifyPhone, 'send'))

    def test_it_send_method_is_callable(self):
        self.assertTrue(callable(VerifyPhone.send))

    def test_send_method_signature(self):
        expected_signature = ['self']
        actual_signature = inspect.getfullargspec(VerifyPhone.send)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_it_has_check_method(self):
        self.assertTrue(hasattr(VerifyPhone, 'check'))

    def test_it_check_method_is_callable(self):
        self.assertTrue(callable(VerifyPhone.check))

    def test_check_method_signature(self):
        expected_signature = ['self', 'code']
        actual_signature = inspect.getfullargspec(VerifyPhone.check)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_it_has_last_otp_expired_method(self):
        self.assertTrue(hasattr(VerifyPhone, 'last_otp_expired'))

    def test_it_last_otp_expired_method_is_callable(self):
        self.assertTrue(callable(VerifyPhone.last_otp_expired))

    def test_last_otp_expired_method_signature(self):
        expected_signature = ['self']
        actual_signature = inspect.getfullargspec(VerifyPhone.last_otp_expired)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_it_has_set_cache_otp_expiry_method(self):
        self.assertTrue(hasattr(VerifyPhone, 'set_cache_otp_expiry'))

    def test_it_set_cache_otp_expiry_method_is_callable(self):
        self.assertTrue(callable(VerifyPhone.set_cache_otp_expiry))

    def test_set_cache_otp_expiry_method_signature(self):
        expected_signature = ['self']
        actual_signature = inspect.getfullargspec(VerifyPhone.set_cache_otp_expiry)[0]
        self.assertEquals(actual_signature, expected_signature)


class VerifyPhoneInitTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.user_phone_model = UserPhone.objects.create(user=self.user, phone=self.user.phone)
        self._class = VerifyPhone(self.user, self.user.phone)

    def test_it_sets_user_to_user_parameter(self):
        self.assertEquals(self.user, self._class.user)

    def test_it_sets_phone_to_phone_parameter(self):
        self.assertEquals(self.user.phone, self._class.phone)

    def test_it_sets_otp_cache_expiry_timestamp(self):
        self.assertEquals(self._class.otp_cache_expiry_timestamp, "{}-otp-cache-expiry-timestamp".format(self.user.id))

    @override_settings(USER_PHONE_MODEL="dj_accounts.authentication.tests.models.UserPhone")
    def test_it_sets_phone_model_to_settings_user_phone_model(self):
        _class = VerifyPhone(self.user, self.user.phone)
        self.assertEquals(_class.phone_model, UserPhone)

    def test_it_sets_phone_object_to_user_if_settings_user_phone_model_is_not_provided(self):
        self.assertEquals(self._class.phone_object, self.user)

    @override_settings(USER_PHONE_MODEL="dj_accounts.authentication.tests.models.UserPhone")
    def test_it_sets_phone_object_to_user_phone_if_settings_user_phone_model_is_provided(self):
        _class = VerifyPhone(self.user, self.user.phone)
        self.assertEquals(_class.phone_object, self.user_phone_model)

    @override_settings(USER_PHONE_MODEL="dj_accounts.authentication.tests.models.UserPhone")
    def test_it_raises_ObjectDoesNotExist_exception_if_phone_does_not_exist(self):
        with self.assertRaises(ObjectDoesNotExist) as e:
            user = UserFactory()
            _class = VerifyPhone(user, user.phone)
            self.assertEquals(e.exception, _("Phone Not Found!"))

    @override_settings(PHONE_VERIFY_SERVICE="dj_accounts.authentication.tests.mocks.MockVerifyService")
    def test_it_sets_service_to_an_instance_of_settings_phone_verify_service_class(self):
        self.assertIsInstance(self._class.service, MockVerifyService)

    def test_it_sets_service_to_BaseVerifyPhoneService_if_settings_phone_verify_service_is_not_provided(self):
        self.assertIsInstance(self._class.service, BaseVerifyPhoneService)


class VerifyPhoneLastOTPExpiredTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self._class = VerifyPhone(self.user, self.user.phone)
        self.otp_cache_key = "{}-otp-cache-expiry-timestamp".format(self.user.id)

    def test_it_returns_false_if_otp_cache_key_is_not_expired(self):
        cache.set(self.otp_cache_key, now().timestamp(), 60)
        self.assertFalse(self._class.last_otp_expired())
        cache.delete(self.otp_cache_key)

    def test_it_returns_true_if_otp_cache_key_is_expired_or_does_not_exist_in_cache(self):
        self.assertTrue(self._class.last_otp_expired())


class VerifyPhoneSetCacheOTPExpiryTestCase(TestCase):
    # TODO Test cache expiration and value as timestamp
    def setUp(self):
        self.user = UserFactory()
        self._class = VerifyPhone(self.user, self.user.phone)
        self.otp_cache_key = "{}-otp-cache-expiry-timestamp".format(self.user.id)

    def tearDown(self):
        cache.delete(self.otp_cache_key)

    def test_it_sets_otp_cache_key(self):
        self._class.set_cache_otp_expiry()
        self.assertIsNotNone(cache.get(self.otp_cache_key))


class VerifyPhoneSendTestCase(TestCase):
    @override_settings(PHONE_VERIFY_SERVICE='dj_accounts.authentication.tests.mocks.MockVerifyService')
    def setUp(self):
        self.user = UserFactory()
        self._class = VerifyPhone(self.user, self.user.phone)
        self.otp_cache_key = "{}-otp-cache-expiry-timestamp".format(self.user.id)

    def tearDown(self):
        cache.delete(self.otp_cache_key)

    @patch('dj_accounts.authentication.tests.mocks.MockVerifyService.send', autospec=True)
    def test_calls_service_send_if_last_otp_cache_key_is_expired(self, mocked_method):
        self._class.send()
        self.assertTrue(mocked_method.called)

    @patch('dj_accounts.authentication.verify_phone.VerifyPhone.set_cache_otp_expiry', autospec=True)
    def test_calls_set_cache_otp_expiry_if_last_otp_cache_key_is_expired(self, mocked_method):
        self._class.send()
        self.assertTrue(mocked_method.called)

    @patch('dj_accounts.authentication.tests.mocks.MockVerifyService.send', autospec=True)
    def test_it_does_not_call_send_if_last_otp_cache_key_is_not_expired(self, mocked_method):
        self._class.set_cache_otp_expiry()
        self._class.send()
        self.assertFalse(mocked_method.called)

    @patch('dj_accounts.authentication.verify_phone.VerifyPhone.set_cache_otp_expiry', autospec=True)
    def test_it_does_not_call_set_cache_otp_expiry_if_last_otp_cache_key_is_not_expired(self, mocked_method):
        cache.set(self.otp_cache_key, now().timestamp(), 60)
        self._class.send()
        self.assertFalse(mocked_method.called)


class VerifyPhoneCheckTestCase(TestCase):
    @override_settings(PHONE_VERIFY_SERVICE='dj_accounts.authentication.tests.mocks.MockVerifyService')
    def setUp(self):
        self.user = UserFactory()
        self._class = VerifyPhone(self.user, self.user.phone)
        self.otp_cache_key = "{}-otp-cache-expiry-timestamp".format(self.user.id)

    def tearDown(self):
        cache.delete(self.otp_cache_key)

    @patch('dj_accounts.authentication.tests.mocks.MockVerifyService.check', autospec=True)
    def test_it_calls_service_check_for_the_provided_code(self, mocked_method):
        self._class.check('1231231')
        self.assertTrue(mocked_method.called)

    @patch('dj_accounts.authentication.tests.models.User.verify_phone', autospec=True)
    def test_it_calls_phone_object_verify_phone_if_code_is_valid(self, mocked_method):
        self._class.check(self._class.service.otp.get())
        self.assertTrue(mocked_method.called)

    def test_it_returns_true_if_provided_code_is_valid(self):
        valid = self._class.check(self._class.service.otp.get())
        self.assertTrue(valid)

    def test_it_returns_false_if_provided_code_is_invalid(self):
        valid = self._class.check('0000000')
        self.assertFalse(valid)

    def test_it_removes_otp_cache_key_from_cache_if_exists_in_cache_and_if_code_is_valid(self):
        self._class.check(self._class.service.otp.get())
        self.assertIsNone(cache.get(self.otp_cache_key))

