from django.urls import path, include


urlpatterns = [
    # accounts urls
    path('', include('accounts.urls.api_urls.urls_auth_api')),
    path('', include('accounts.urls.api_urls.urls_profile_api')),
]
