from django.urls import path, include

app_name = 'api-v1'

urlpatterns = [
    # accounts urls
    path('', include('accounts.urls_auth_api')),
    path('', include('accounts.urls_profile_api')),

]
