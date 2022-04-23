from django.contrib import admin
from django.urls import include, path

api_urlpatterns = [
    ('auth/', 'apps.auth.urls'),
]
urlpatterns = [
    path('admin/', admin.site.urls),
] + [
    path('api/v1/' + path_str, include(urlpatterns))
    for path_str, urlpatterns in api_urlpatterns
]
