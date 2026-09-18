from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("admin-mobile/", include("django_admin_mobile.urls")),
]
