from django.urls import path

from dj_accounts.social.views_api import SocialLoginAPIView

app_name = "social"

urlpatterns = [
    path('<str:provider_name>/', SocialLoginAPIView.as_view(), name="login"),
]
