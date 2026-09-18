"""Costruzione della struttura dati del menu mobile.

L'admin di Django mette in ogni pagina (via ``AdminSite.each_context``) la
chiave ``available_apps``: l'elenco delle app e dei modelli che l'utente
collegato può vedere. Da lì ricaviamo tutto il menu, così la shell mobile
resta sempre allineata ai permessi senza che il progetto debba dichiarare
niente a mano.

Il risultato è un dizionario serializzabile in JSON che viene consegnato al
browser dentro la pagina; il JavaScript del pacchetto lo usa per costruire
la barra in alto, la barra in basso e il menu laterale.
"""

from django.db import DatabaseError
from django.urls import NoReverseMatch, reverse
from django.utils.encoding import force_str

from .conf import get_config
from .models import MenuIcon


#: Icone di partenza per le app più comuni. Si sovrascrivono dal database
#: (modello ``MenuIcon``) oppure dal setting ``ADMIN_MOBILE["APP_ICONS"]``.
DEFAULT_APP_ICONS = {
    "admin": "⚙️",
    "auth": "🔐",
    "authtoken": "🔑",
    "blog": "✍️",
    "calendario": "🗓️",
    "chatbot": "🤖",
    "consent": "📜",
    "contenttypes": "🧩",
    "flatpages": "📃",
    "frontend": "🌐",
    "impostazioni": "🛠️",
    "pazienti": "🧑‍⚕️",
    "posta": "✉️",
    "sessions": "💾",
    "sites": "🌍",
    "social": "📣",
    "visite": "📅",
    "whatsapp_bot": "💬",
}

DEFAULT_COLOR = "#417690"
DEFAULT_BG = "#ffffff"


def _load_icons():
    """Icone configurate a database, tolleranti alla tabella non ancora creata."""
    try:
        return MenuIcon.objects.filter(visible=True).as_map()
    except DatabaseError:
        # Migrazione non ancora applicata (o database non raggiungibile):
        # la shell deve comunque funzionare con i default.
        return {}


def _resolve(icons, app_label, model_name=""):
    """Configurazione più specifica disponibile: prima il modello, poi l'app."""
    return icons.get((app_label, (model_name or "").lower())) or icons.get((app_label, ""))


def _icon_for(cfg, app_label, config):
    if cfg and cfg.icon:
        return cfg.icon
    app_icons = dict(DEFAULT_APP_ICONS)
    app_icons.update(config.get("APP_ICONS") or {})
    return app_icons.get(app_label) or config.get("FALLBACK_ICON") or "📄"


def _text(value):
    """I nomi dei modelli sono stringhe di traduzione pigre: qui servono
    stringhe vere, altrimenti il menu non è serializzabile in JSON."""
    return force_str(value) if value is not None else None


def _reverse(url_name, args=None):
    try:
        return reverse(url_name, args=args or [])
    except NoReverseMatch:
        return None


def build_items(app_list, config=None):
    """Appiattisce ``app_list`` in un elenco ordinato di voci di menu.

    Ogni voce è un dizionario con: ``label``, ``url``, ``icon``, ``color``,
    ``background``, ``order``, ``pinned``, ``app_label``, ``app_name`` e
    ``add_url`` (``None`` se l'utente non può aggiungere).
    """
    config = config or get_config()
    icons = _load_icons()
    excluded_apps = set(config.get("EXCLUDE_APPS") or [])
    excluded_models = {m.lower() for m in (config.get("EXCLUDE_MODELS") or [])}

    items = []
    for app in app_list or []:
        app_label = app.get("app_label") or ""
        if app_label in excluded_apps:
            continue
        app_name = _text(app.get("name")) or app_label
        for model in app.get("models") or []:
            model_key = (model.get("object_name") or "").lower()
            if f"{app_label}.{model_key}" in excluded_models:
                continue
            url = model.get("admin_url") or model.get("add_url")
            if not url:
                # Modello senza alcuna pagina raggiungibile: inutile mostrarlo.
                continue
            cfg = _resolve(icons, app_label, model_key)
            label = cfg.label_override if cfg and cfg.label_override else (model.get("name") or model_key)
            items.append(
                {
                    "label": _text(label),
                    "url": _text(url),
                    "add_url": _text(model.get("add_url")) or None,
                    "icon": _text(_icon_for(cfg, app_label, config)),
                    "color": _text(cfg.color if cfg else DEFAULT_COLOR),
                    "background": _text(cfg.background if cfg else DEFAULT_BG),
                    "order": (cfg.order if cfg else 0),
                    "pinned": bool(cfg.pinned) if cfg else False,
                    "app_label": _text(app_label),
                    "app_name": _text(app_name),
                }
            )

    items.sort(key=lambda i: (i["order"], i["app_name"], i["label"]))
    return items


def build_groups(items):
    """Raggruppa le voci per app, mantenendo l'ordine di ``items``."""
    groups = []
    index = {}
    for item in items:
        key = item["app_label"]
        if key not in index:
            index[key] = {"app_label": key, "name": item["app_name"], "items": []}
            groups.append(index[key])
        index[key]["items"].append(item)
    return groups


def build_tabs(items, config=None, home_url="/admin/"):  # noqa: C901
    """Voci della barra in basso.

    Se ``ADMIN_MOBILE["TABS"]`` è valorizzato vince quello (e può puntare a
    qualsiasi URL del progetto, non solo a pagine dell'admin). Altrimenti si
    usano le voci marcate "in evidenza"; se non ce n'è nessuna si prendono le
    prime dell'elenco, così la barra non è mai vuota.
    """
    config = config or get_config()
    max_tabs = max(2, int(config.get("MAX_TABS") or 5))

    explicit = config.get("TABS") or []
    if explicit:
        tabs = []
        for entry in explicit:
            url = entry.get("url")
            if not url and entry.get("url_name"):
                url = _reverse(entry["url_name"], entry.get("args"))
            if not url:
                # Indirizzo inesistente in questo progetto: si salta la voce
                # invece di rompere tutta la barra.
                continue
            tab = {
                "label": _text(entry.get("label")) or "",
                "url": _text(url),
                "icon": _text(entry.get("icon")) or "•",
                "match": _text(entry.get("match") or url),
            }
            # La home dell'admin è prefisso di ogni altra pagina: va
            # confrontata per intero, altrimenti risulterebbe sempre attiva.
            if entry.get("exact") or url == home_url:
                tab["exact"] = True
            tabs.append(tab)
        return tabs[:max_tabs]

    home = {"label": "Home", "url": home_url, "icon": "🏠", "match": home_url, "exact": True}
    pinned = [i for i in items if i["pinned"]]
    chosen = pinned or items
    slots = max_tabs - 2  # una per Home, una per Menu
    tabs = [home]
    for item in chosen[:slots]:
        tabs.append(
            {
                "label": item["label"],
                "url": item["url"],
                "icon": item["icon"],
                "match": item["url"],
            }
        )
    return tabs


def build_menu(context=None, app_list=None, config=None):
    """Struttura completa passata al JavaScript della shell."""
    config = config or get_config()
    context = context or {}

    if app_list is None:
        app_list = context.get("available_apps") or context.get("app_list") or []

    home_url = _reverse("admin:index") or "/admin/"
    items = build_items(app_list, config=config)

    user = context.get("user")
    username = ""
    if user is not None and getattr(user, "is_authenticated", False):
        username = force_str(user.get_short_name() or user.get_username())

    return {
        "breakpoint": config.get("BREAKPOINT"),
        "accent": config.get("ACCENT"),
        "title": config.get("TITLE") or str(context.get("site_header") or "Amministrazione"),
        "features": {
            "appbar": bool(config.get("APPBAR")),
            "tabbar": bool(config.get("TABBAR")),
            "drawer": bool(config.get("DRAWER")),
            "cards": bool(config.get("CARDS")),
            "filterSheet": bool(config.get("FILTER_SHEET")),
            "fab": bool(config.get("FAB")),
            "forms": bool(config.get("FORMS")),
            "hideChrome": bool(config.get("HIDE_DJANGO_CHROME")),
        },
        "urls": {
            "home": home_url,
            "site": context.get("site_url") or "/",
            "password": _reverse("admin:password_change"),
            "logout": _reverse("admin:logout"),
        },
        "user": {"name": _text(username), "initial": (username[:1] or "?").upper()},
        "tabs": build_tabs(items, config=config, home_url=home_url),
        "groups": build_groups(items),
        "labels": {
            "menu": "Menu",
            "back": "Indietro",
            "search": "Cerca",
            "searchMenu": "Cerca una sezione…",
            "filters": "Filtri",
            "actions": "Azioni",
            "apply": "Applica",
            "close": "Chiudi",
            "add": "Aggiungi",
            "site": "Vedi il sito",
            "password": "Cambia password",
            "logout": "Esci",
            "theme": "Tema",
            "noResults": "Nessuna sezione trovata.",
            "allSections": "Tutte le sezioni",
            "selected": "selezionati",
        },
    }
