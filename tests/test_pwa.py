"""Installazione dell'admin come app sul telefono."""

import json

import pytest
from django.template import Context, Template
from django.test import override_settings

from django_admin_mobile import pwa


@pytest.mark.django_db
def test_manifest_view_describes_the_app(client):
    response = client.get("/admin-mobile/manifest.webmanifest")
    assert response.status_code == 200
    assert response["Content-Type"] == "application/manifest+json"
    data = json.loads(response.content)
    assert data["start_url"] == "/admin/"
    assert data["scope"] == "/admin/"
    assert data["display"] == "standalone"
    assert data["icons"], "senza icone il browser non propone l'installazione"


@pytest.mark.django_db
@override_settings(ADMIN_MOBILE={"PWA_ICONS": [
    {"src": "img/app-192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "https://cdn.example/app-512.png", "sizes": "512x512", "type": "image/png"},
]})
def test_manifest_accepts_static_paths_and_absolute_urls(client):
    data = json.loads(client.get("/admin-mobile/manifest.webmanifest").content)
    sources = [i["src"] for i in data["icons"]]
    assert sources[0] == "/static/img/app-192.png"
    assert sources[1] == "https://cdn.example/app-512.png"


@pytest.mark.django_db
def test_service_worker_is_allowed_to_govern_the_admin(client):
    """Senza questa intestazione il file non potrebbe controllare /admin/."""
    response = client.get("/admin-mobile/sw.js")
    assert response.status_code == 200
    assert response["Service-Worker-Allowed"] == "/admin/"
    assert "text/javascript" in response["Content-Type"]
    body = response.content.decode()
    assert "addEventListener" in body and "fetch" in body


@pytest.mark.django_db
def test_service_worker_never_serves_pages_from_cache(client):
    """In un gestionale i dati vecchi fanno più danno della lentezza."""
    body = client.get("/admin-mobile/sw.js").content.decode()
    navigate = body[body.index('request.mode === "navigate"'):]
    # Per le pagine si va in cache solo dopo che la rete ha fallito.
    assert "fetch(request).catch" in navigate


@pytest.mark.django_db
def test_fallback_icon_and_offline_page(client):
    icon = client.get("/admin-mobile/icon.svg")
    assert icon.status_code == 200
    assert icon["Content-Type"] == "image/svg+xml"
    assert b"<svg" in icon.content

    offline = client.get("/admin-mobile/offline/")
    assert offline.status_code == 200
    assert "connessione" in offline.content.decode().lower()


@override_settings(ADMIN_MOBILE={"ACCENT": "javascript:alert(1)"})
@pytest.mark.django_db
def test_fallback_icon_refuses_a_bogus_colour(client):
    body = client.get("/admin-mobile/icon.svg").content.decode()
    assert "javascript:" not in body
    assert "#417690" in body


def test_short_name_is_trimmed_to_fit_under_the_icon():
    config = {"PWA_NAME": "Gestionale Operativo Dottor Rossi", "TITLE": None}
    assert pwa.short_name(config) == "Gestionale"


def test_short_name_respects_an_explicit_value():
    assert pwa.short_name({"PWA_SHORT_NAME": "Studio", "PWA_NAME": "Qualcosa"}) == "Studio"


@pytest.mark.django_db
def test_assets_tag_publishes_the_manifest():
    html = Template("{% load admin_mobile %}{% mobile_admin_assets %}").render(Context({}))
    assert 'rel="manifest"' in html
    assert "/admin-mobile/manifest.webmanifest" in html
    assert 'name="apple-mobile-web-app-capable"' in html


@override_settings(ADMIN_MOBILE={"PWA": False})
@pytest.mark.django_db
def test_assets_tag_stays_silent_when_the_pwa_is_off():
    html = Template("{% load admin_mobile %}{% mobile_admin_assets %}").render(Context({}))
    assert "manifest" not in html
    assert "admin_mobile.css" in html      # il resto continua a funzionare


@override_settings(ROOT_URLCONF="tests.urls_without_pwa")
@pytest.mark.django_db
def test_pwa_degrades_when_urls_are_not_included():
    """Il pacchetto deve funzionare anche se il progetto non include gli URL."""
    assert pwa.is_enabled() is False
    assert pwa.context() is None
    html = Template("{% load admin_mobile %}{% mobile_admin_assets %}").render(Context({}))
    assert "manifest" not in html
