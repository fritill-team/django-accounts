from abc import abstractmethod, ABC
from datetime import timedelta

import pyotp
from django.core.cache import cache
from django.utils.timezone import now

from dj_accounts.utils import get_settings_value, get_class_from_settings


class BaseOTP:
    def __init__(self, user):
        self.user = user
        self.otp = None
        self.initialize()

    @abstractmethod
    def verify(self, otp):
        raise NotImplementedError

    @abstractmethod
    def get(self):
        raise NotImplementedError

    @abstractmethod
    def initialize(self):
        raise NotImplementedError

    def authenticate(self, otp):
        provided_otp = 0
        try:
            provided_otp = int(otp)
        except:
            return False

        return self.verify(provided_otp)


class HOTP(BaseOTP):
    def initialize(self):
        self.otp = pyotp.HOTP(
            self.user.key,
            digits=get_settings_value("PHONE_VERIFICATION_CODE_LENGTH", 6), )

    def get(self):
        return self.otp.at(self.user.otp_counter)

    def verify(self, otp):
        is_valid = self.otp.verify(str(otp), self.user.otp_counter)
        if is_valid:
            self.user.otp_counter += 1
            self.user.save()
        return is_valid


class TOTP(BaseOTP):
    def initialize(self):
        self.otp = pyotp.TOTP(
            self.user.key,
            digits=get_settings_value("PHONE_VERIFICATION_CODE_LENGTH", 6),
            interval=get_settings_value('PHONE_VERIFICATION_CODE_INTERVAL', 60))

    def get(self):
        return self.otp.now()

    def verify(self, otp):
        return self.otp.verify(otp)


OTP_TYPES = {
    "HOTP": HOTP,
    "TOTP": TOTP
}


def get_otp_class():
    settings_otp = get_settings_value('OTP_VERIFICATION_TYPE', "TOTP")

    if settings_otp not in OTP_TYPES.keys():
        raise KeyError("OTP_VERIFICATION_TYPE is not valid, it must be HOTP or TOTP")

    return OTP_TYPES.get(settings_otp)


class BaseVerifyPhoneService:

    def __init__(self, user, phone):
        self.user = user
        self.phone = phone
        self.otp = get_otp_class()(user)

    @abstractmethod
    def send(self):
        pass

    @abstractmethod
    def check(self, code):
        pass


class VerifyPhone:
    def __init__(self, user, phone):
        self.user = user
        self.phone = phone
        self.otp_cache_expiry_timestamp = "{}-otp-cache-expiry-timestamp".format(self.user.id)
        self.phone_model = get_settings_value('USER_PHONE_MODEL')
        self.phone_object = user
        if self.phone_model:
            self.phone_object = self.phone_model.objects.filter(phone=phone, user=user)
            if not self.phone_object.exists():
                raise Exception

        self.service = get_class_from_settings(
            'PHONE_VERIFY_SERVICE', 'dj_accounts.authentication.verify_phone.BaseVerifyPhoneService')(user, phone)

    def last_otp_expired(self):
        return not cache.get(self.otp_cache_expiry_timestamp)

    def set_cache_otp_expiry(self):
        interval = get_settings_value("PHONE_VERIFICATION_CODE_INTERVAL", 60)
        timestamp = now() + timedelta(seconds=interval)
        cache.set(self.otp_cache_expiry_timestamp, timestamp.timestamp(), interval)

    def send(self):
        if self.last_otp_expired():
            self.service.send()
            self.set_cache_otp_expiry()

    def check(self, code):
        if self.service.check(code):
            self.phone_object.verify_phone()
            if not self.last_otp_expired():
                cache.delete(self.otp_cache_expiry_timestamp)
            return True
        return False
