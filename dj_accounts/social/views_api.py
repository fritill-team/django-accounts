from django.contrib.auth import login
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .providers import get_provider


class SocialLoginAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, provider_name, *args, **kwargs):
        success, user_or_errors, new_account = get_provider(provider_name)(request.data).get_user()
        if success:
            login(request, user_or_errors)
            tokens = RefreshToken.for_user(user_or_errors)
            return Response({
                "access_token": str(tokens.access_token),
                "refresh_token": str(tokens),
                "new_account": new_account
            }, status=status.HTTP_200_OK)

        return Response(user_or_errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
