"""Viste che servono i file necessari all'installazione come app."""

import json

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET

from . import pwa
from .conf import get_config


@require_GET
@cache_control(max_age=3600)
def manifest(request):
    """Il manifest dell'app, costruito dalle impostazioni del progetto."""
    return JsonResponse(
        pwa.manifest(),
        content_type="application/manifest+json",
        json_dumps_params={"ensure_ascii": False},
    )


@require_GET
def service_worker(request):
    """Service worker.

    Va servito da una vista e non da ``/static/``: solo così si può mandare
    l'intestazione ``Service-Worker-Allowed``, senza la quale il file non
    potrebbe governare le pagine dell'admin (che stanno fuori da /static/).
    """
    config = get_config()
    scope = config.get("PWA_SCOPE") or pwa._admin_home()
    body = render_to_string(
        "django_admin_mobile/sw.js",
        {
            "cache_name": "dam-{}".format(config.get("PWA_CACHE_VERSION") or "1"),
            "offline_url": pwa._url("offline") or "",
            "static_url": json.dumps(getattr(settings, "STATIC_URL", "/static/") or "/static/"),
        },
    )
    response = HttpResponse(body, content_type="text/javascript")
    response["Service-Worker-Allowed"] = scope
    # Il browser deve accorgersi subito di una versione nuova.
    response["Cache-Control"] = "no-cache"
    return response


@require_GET
@cache_control(max_age=86400)
def icon(request):
    """Icona di ripiego: un quadrato con il colore dell'app e un'iniziale.

    Serve solo quando il progetto non dichiara ``PWA_ICONS``; per un risultato
    curato conviene sempre fornire dei PNG veri.
    """
    config = get_config()
    accent = config.get("ACCENT") or "#417690"
    if not _is_hex(accent):
        accent = "#417690"
    letter = (pwa.short_name(config)[:1] or "A").upper()
    svg = render_to_string(
        "django_admin_mobile/icon.svg",
        {"accent": accent, "letter": letter},
    )
    return HttpResponse(svg, content_type="image/svg+xml")


@require_GET
def offline(request):
    """Pagina mostrata quando si apre l'app senza connessione."""
    config = get_config()
    accent = config.get("ACCENT") or "#417690"
    if not _is_hex(accent):
        accent = "#417690"
    return HttpResponse(
        render_to_string(
            "django_admin_mobile/offline.html",
            {"accent": accent, "name": pwa.app_name(config)},
        )
    )


def _is_hex(value):
    value = str(value or "")
    if not value.startswith("#") or len(value) not in (4, 7, 9):
        return False
    return all(c in "0123456789abcdefABCDEF" for c in value[1:])
