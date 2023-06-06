from django.contrib.auth import get_user_model
from rest_framework import serializers


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name']


def profile_serializer_handler():
    return ProfileSerializer
