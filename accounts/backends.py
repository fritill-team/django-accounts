from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()


class MultipleAuthenticationBackend(ModelBackend):
    def authenticate(self, request, **kwargs):
        query = None


        # try:
        #     user = UserModel.objects.get(**query)
        # except UserModel.DoesNotExist:
        #     # Run the default password hasher once to reduce the timing
        #     # difference between an existing and a nonexistent user (#20760).
        #     UserModel().set_password(password)
        # else:
        #     if user.check_password(password) and self.user_can_authenticate(user):
        #         return user
