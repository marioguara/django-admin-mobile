"""Tag da usare nei template dell'admin.

Nel `base.html` dell'admin (o in un suo override) basta una riga::

    {% load admin_mobile %}
    {% mobile_admin_assets %}

Da lì il pacchetto si occupa di tutto: CSS, dati del menu e JavaScript che
costruisce la shell mobile (barra in alto, barra in basso, menu laterale).
"""

import json

from django import template
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from ..conf import get_config
from ..menu import (  # noqa: F401  (riesportati per compatibilità)
    DEFAULT_APP_ICONS,
    DEFAULT_BG,
    DEFAULT_COLOR,
    build_items,
    build_menu,
)


register = template.Library()

#: id dell'elemento <script> che porta il menu al browser.
CONFIG_ELEMENT_ID = "dam-config"


def _config_script(context):
    """Serializza il menu in un `<script type="application/json">`.

    Dopo `json.dumps` si neutralizzano i caratteri che potrebbero chiudere il
    tag `<script>` in anticipo: è la stessa difesa del filtro `json_script` di
    Django, riscritta qui per non dipendere dalla versione.
    """
    payload = json.dumps(build_menu(context), ensure_ascii=False, cls=DjangoJSONEncoder)
    payload = (
        payload.replace("<", "\\u003C")
        .replace(">", "\\u003E")
        .replace("&", "\\u0026")
    )
    return format_html(
        '<script id="{}" type="application/json">{}</script>',
        CONFIG_ELEMENT_ID,
        mark_safe(payload),  # i caratteri pericolosi sono già stati sostituiti
    )


@register.simple_tag(takes_context=True)
def mobile_admin_config(context):
    """Solo i dati del menu, per chi vuole posizionarli a mano."""
    return _config_script(context)


@register.inclusion_tag("django_admin_mobile/_mobile_assets.html", takes_context=True)
def mobile_admin_assets(context):
    """CSS, dati del menu e JavaScript della shell mobile."""
    return {
        "dam_config": _config_script(context),
        "accent": get_config().get("ACCENT"),
    }


@register.inclusion_tag("django_admin_mobile/_mobile_menu.html", takes_context=True)
def render_mobile_menu(context, app_list=None):
    """Griglia di icone in stile schermata home di un telefono.

    Se `app_list` non viene passato si legge dal context (`app_list` oppure
    `available_apps`, come li fornisce l'admin di Django).
    """
    if app_list is None:
        app_list = context.get("app_list") or context.get("available_apps") or []

    config = get_config()
    items = build_items(app_list, config=config)
    return {
        "tiles": items,
        "groups": _group(items),
        "accent": config.get("ACCENT"),
    }


def _group(items):
    """Raggruppa le voci per app mantenendo l'ordine ricevuto."""
    groups = []
    index = {}
    for item in items:
        key = item["app_label"]
        if key not in index:
            index[key] = {"app_label": key, "name": item["app_name"], "items": []}
            groups.append(index[key])
        index[key]["items"].append(item)
    return groups
