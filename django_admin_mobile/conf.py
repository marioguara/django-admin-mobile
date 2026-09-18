"""Configurazione del pacchetto.

Tutto si regola da un unico dizionario nei settings del progetto::

    ADMIN_MOBILE = {
        "ACCENT": "#074674",
        "TABS": [
            {"url_name": "admin:index", "icon": "🏠", "label": "Home"},
            {"url_name": "admin:pazienti_paziente_changelist", "icon": "👥"},
        ],
    }

Ogni chiave non indicata usa il valore di ``DEFAULTS``.
"""

from django.conf import settings


DEFAULTS = {
    # Larghezza massima (px) sotto la quale si attiva l'interfaccia mobile.
    "BREAKPOINT": 1024,
    # Colore principale dell'app (barre, stati attivi, bottone azione).
    "ACCENT": "#417690",
    # Titolo mostrato nella barra in alto; None = nome del sito admin.
    "TITLE": None,
    # Componenti della shell: si possono spegnere uno per uno.
    "APPBAR": True,
    "TABBAR": True,
    "DRAWER": True,
    "CARDS": True,
    "FILTER_SHEET": True,
    "FAB": True,
    "FORMS": True,
    # Nasconde header, breadcrumb e sidebar nativi di Django su mobile.
    "HIDE_DJANGO_CHROME": True,
    # Numero massimo di voci nella barra in basso (Home e Menu inclusi).
    "MAX_TABS": 5,
    # Voci della barra in basso. Vuoto = ricavate dalle icone "in evidenza".
    # Ogni voce: {"url_name" o "url", "label", "icon", "match"}.
    "TABS": [],
    # App e modelli da tenere fuori dal menu mobile.
    # EXCLUDE_MODELS accetta "app_label.modelname".
    "EXCLUDE_APPS": [],
    "EXCLUDE_MODELS": [],
    # Icone di default aggiuntive per app: {"app_label": "🧩"}.
    "APP_ICONS": {},
    # Icona usata quando non se ne trova una più specifica.
    "FALLBACK_ICON": "📄",

    # ── Installazione come app (PWA) ──────────────────────────────────────
    # Richiede di includere django_admin_mobile.urls negli URL del progetto.
    "PWA": True,
    "PWA_PROMPT": True,          # mostra l'invito a installare su telefono
    "PWA_NAME": None,            # None = TITLE
    "PWA_SHORT_NAME": None,      # None = le prime parole di PWA_NAME
    "PWA_DESCRIPTION": "",
    # Icone: percorsi statici ("img/icona-192.png") oppure indirizzi assoluti.
    # Senza icone il pacchetto ne genera una con il colore e l'iniziale.
    "PWA_ICONS": [],
    "PWA_START_URL": None,       # None = pagina iniziale dell'admin
    "PWA_SCOPE": None,           # None = pagina iniziale dell'admin
    "PWA_DISPLAY": "standalone",
    "PWA_ORIENTATION": "portrait",
    "PWA_BACKGROUND": "#ffffff",
    # Cambia questo valore per invalidare la cache del service worker.
    "PWA_CACHE_VERSION": "1",
}


def get_config():
    """Restituisce i settings del pacchetto con i default già applicati."""
    config = dict(DEFAULTS)
    config.update(getattr(settings, "ADMIN_MOBILE", None) or {})
    return config


def get_setting(name):
    """Comodità per leggere una singola chiave."""
    return get_config().get(name, DEFAULTS.get(name))
