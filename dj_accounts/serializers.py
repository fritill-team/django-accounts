from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm, PasswordChangeForm
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

UserModel = get_user_model()



class UpdateUserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name']


class UpdateEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['email', 'password']


class UpdatePhoneNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['phone', 'password']


class ChangePasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['new_password1', 'new_password2', 'old_password']

    new_password1 = serializers.CharField(required=True, write_only=True)
    new_password2 = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    old_password = serializers.CharField(required=True, write_only=True)
    form = None

    def validate(self, data):
        self.form = PasswordChangeForm(data=data, user=self.context['request'].user)
        if not self.form.is_valid():
            serializers.ValidationError(self.form.errors)
        return data

    def save(self, **kwargs):
        self.form.save()
