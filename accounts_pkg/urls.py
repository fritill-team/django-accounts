from django.urls import path, include

urlpatterns = [
    # add account profile
    path('', include('dj_accounts.urls.site_urls.urls_profile')),
    path('', include('dj_accounts.urls.site_urls.urls_auth')),
    # include api urls
    path('api/', include('dj_accounts.urls.api_urls.urls_auth_api')),
    path('api/', include('dj_accounts.urls.api_urls.urls_profile_api')),
]
