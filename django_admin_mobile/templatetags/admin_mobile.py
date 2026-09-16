from django import template
from django.db import OperationalError, ProgrammingError

from ..models import MenuIcon


register = template.Library()

# Icone di default per app comuni. Sovrascrivibili dal modello MenuIcon.
DEFAULT_APP_ICONS = {
    "auth": "🔐",
    "authtoken": "🔑",
    "sites": "🌍",
    "admin": "⚙️",
    "contenttypes": "🧩",
    "sessions": "💾",
    "pazienti": "🧑‍⚕️",
    "visite": "📅",
    "calendario": "🗓️",
    "blog": "✍️",
    "chatbot": "🤖",
    "whatsapp_bot": "💬",
    "posta": "✉️",
    "social": "📣",
    "consent": "📜",
    "impostazioni": "🛠️",
    "frontend": "🌐",
}

DEFAULT_COLOR = "#417690"
DEFAULT_BG = "#ffffff"


def _load_icons():
    """Restituisce {(app_label, model_name_or_empty): MenuIcon}."""
    try:
        qs = MenuIcon.objects.filter(visible=True)
        return {(mi.app_label, mi.model_name.lower()): mi for mi in qs}
    except (OperationalError, ProgrammingError):
        # Tabella non ancora migrata: degrada silenziosamente ai default.
        return {}


def _resolve_icon(icons, app_label, model_name):
    return (
        icons.get((app_label, model_name.lower()))
        or icons.get((app_label, ""))
    )


@register.inclusion_tag("django_admin_mobile/_mobile_menu.html", takes_context=True)
def render_mobile_menu(context, app_list=None):
    """Rende una griglia di bottoni con icone per il menu admin mobile.

    Se `app_list` non è passato, viene letto dal context (chiavi
    `app_list` o `available_apps`, come forniti dall'admin di Django).
    """

    if app_list is None:
        app_list = context.get("app_list") or context.get("available_apps") or []

    icons = _load_icons()
    tiles = []
    for app in app_list:
        app_label = app.get("app_label") or ""
        for model in app.get("models", []) or []:
            model_key = (model.get("object_name") or "").lower()
            cfg = _resolve_icon(icons, app_label, model_key)
            url = model.get("admin_url") or model.get("add_url") or "#"
            tiles.append(
                {
                    "label": (cfg.label_override if cfg and cfg.label_override else model.get("name", model_key)),
                    "url": url,
                    "icon": (cfg.icon if cfg else DEFAULT_APP_ICONS.get(app_label, "📄")),
                    "color": (cfg.color if cfg else DEFAULT_COLOR),
                    "background": (cfg.background if cfg else DEFAULT_BG),
                    "order": (cfg.order if cfg else 0),
                    "app_label": app_label,
                }
            )

    tiles.sort(key=lambda t: (t["order"], t["app_label"], t["label"]))
    return {"tiles": tiles}


@register.inclusion_tag("django_admin_mobile/_mobile_assets.html")
def mobile_admin_assets():
    """Inietta i link agli asset (CSS/JS) del pacchetto."""
    return {}
