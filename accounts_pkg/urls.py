from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    # add account profile
    path('', include('dj_accounts.authentication.urls')),
    path('api/', include('dj_accounts.authentication.urls_api')),
    path('admin/', include('dj_accounts.authentication.urls_admin')),
    # path('', include('dj_accounts.urls.site_urls.urls_auth')),
    # # include api urls
    # path('api/', include('dj_accounts.urls.api_urls.urls_auth_api')),
    # path('api/', include('dj_accounts.urls.api_urls.urls_profile_api')),

    path('i18n/', include('django.conf.urls.i18n')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)