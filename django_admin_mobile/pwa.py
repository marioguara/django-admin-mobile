"""Installazione dell'admin come app sul telefono (PWA).

Perché servono delle viste e non dei file statici: il *service worker* può
controllare solo le pagine che stanno sotto il proprio indirizzo, a meno che
non venga servito con l'intestazione ``Service-Worker-Allowed``. Un file in
``/static/`` non può quindi governare ``/admin/``; una vista sì.

Tutto è facoltativo: se il progetto non include ``django_admin_mobile.urls``
le funzioni qui sotto restituiscono ``None`` e il pacchetto si comporta come
prima, senza errori.
"""

from django.templatetags.static import static
from django.urls import NoReverseMatch, reverse

from .conf import get_config


def _url(name):
    try:
        return reverse(f"admin_mobile:{name}")
    except NoReverseMatch:
        return None


def _admin_home():
    try:
        return reverse("admin:index")
    except NoReverseMatch:
        return "/admin/"


def _icon_src(entry):
    """Accetta sia un percorso statico sia un indirizzo già completo."""
    src = entry.get("src") or ""
    if src.startswith(("http://", "https://", "/")):
        return src
    return static(src)


def is_enabled():
    """La PWA è attiva solo se richiesta e se gli URL sono stati inclusi."""
    return bool(get_config().get("PWA")) and _url("manifest") is not None


def app_name(config=None):
    config = config or get_config()
    return config.get("PWA_NAME") or config.get("TITLE") or "Admin"


def short_name(config=None):
    config = config or get_config()
    explicit = config.get("PWA_SHORT_NAME")
    if explicit:
        return explicit
    # Il nome breve compare sotto l'icona: oltre una dozzina di caratteri
    # viene troncato dal sistema, quindi si tengono le prime parole.
    words = app_name(config).split()
    short = ""
    for word in words:
        candidate = (short + " " + word).strip()
        if len(candidate) > 12 and short:
            break
        short = candidate
    return short or app_name(config)[:12]


def icons(config=None):
    """Icone dichiarate dal progetto, oppure quella generata dal pacchetto."""
    config = config or get_config()
    declared = config.get("PWA_ICONS") or []
    if declared:
        return [
            {
                "src": _icon_src(entry),
                "sizes": entry.get("sizes", "192x192"),
                "type": entry.get("type", "image/png"),
                "purpose": entry.get("purpose", "any"),
            }
            for entry in declared
        ]
    fallback = _url("icon")
    if not fallback:
        return []
    return [{"src": fallback, "sizes": "any", "type": "image/svg+xml", "purpose": "any maskable"}]


def manifest(config=None):
    """Il contenuto del file manifest, come dizionario."""
    config = config or get_config()
    home = _admin_home()
    return {
        "name": app_name(config),
        "short_name": short_name(config),
        "description": config.get("PWA_DESCRIPTION") or "",
        "start_url": config.get("PWA_START_URL") or home,
        "scope": config.get("PWA_SCOPE") or home,
        "display": config.get("PWA_DISPLAY") or "standalone",
        "orientation": config.get("PWA_ORIENTATION") or "portrait",
        "background_color": config.get("PWA_BACKGROUND") or "#ffffff",
        "theme_color": config.get("ACCENT") or "#417690",
        "icons": icons(config),
    }


def context(config=None):
    """Dati passati ai template e al JavaScript. ``None`` se la PWA è spenta."""
    config = config or get_config()
    if not is_enabled():
        return None
    manifest_url = _url("manifest")
    return {
        "manifest_url": manifest_url,
        "sw_url": _url("service_worker"),
        "scope": config.get("PWA_SCOPE") or _admin_home(),
        "name": app_name(config),
        "short_name": short_name(config),
        "icons": icons(config),
        "apple_icon": next((i["src"] for i in icons(config) if i["type"] != "image/svg+xml"), None),
        "prompt": bool(config.get("PWA_PROMPT")),
        "theme_color": config.get("ACCENT") or "#417690",
    }
