from django.urls import path, include

urlpatterns = [
    path('sites/', include('dj_accounts.authentication.urls_sites')),
]