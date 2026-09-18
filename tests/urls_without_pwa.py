"""Un progetto che NON include django_admin_mobile.urls: la PWA va spenta."""

from django.contrib import admin
from django.urls import path

urlpatterns = [path("admin/", admin.site.urls)]
