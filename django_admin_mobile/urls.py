"""Indirizzi per l'installazione come app.

Da includere negli URL del progetto::

    path("admin-mobile/", include("django_admin_mobile.urls")),

Se non vengono inclusi il pacchetto funziona lo stesso: semplicemente l'admin
non è installabile come app.
"""

from django.urls import path

from . import views


app_name = "admin_mobile"

urlpatterns = [
    path("manifest.webmanifest", views.manifest, name="manifest"),
    path("sw.js", views.service_worker, name="service_worker"),
    path("icon.svg", views.icon, name="icon"),
    path("offline/", views.offline, name="offline"),
]
