"""Struttura dati del menu consegnata al browser."""

import json

import pytest
from django.template import Context, Template
from django.utils.translation import gettext_lazy as _

from django_admin_mobile.menu import build_items, build_menu, build_tabs
from django_admin_mobile.models import MenuIcon


APP_LIST = [
    {
        "app_label": "visite",
        "name": "Visite",
        "models": [
            {"name": "Visite", "object_name": "Visita",
             "admin_url": "/admin/visite/visita/", "add_url": "/admin/visite/visita/add/"},
        ],
    },
    {
        "app_label": "pazienti",
        "name": "Pazienti",
        "models": [
            {"name": "Pazienti", "object_name": "Paziente",
             "admin_url": "/admin/pazienti/paziente/"},
            {"name": "Allegati", "object_name": "Allegato",
             "admin_url": "/admin/pazienti/allegato/"},
        ],
    },
]


@pytest.mark.django_db
def test_build_items_flattens_and_keeps_add_url():
    items = build_items(APP_LIST)
    labels = [i["label"] for i in items]
    assert set(labels) == {"Visite", "Pazienti", "Allegati"}
    visite = next(i for i in items if i["label"] == "Visite")
    assert visite["add_url"] == "/admin/visite/visita/add/"
    pazienti = next(i for i in items if i["label"] == "Pazienti")
    assert pazienti["add_url"] is None


@pytest.mark.django_db
def test_build_items_skips_models_without_any_url():
    app_list = [{"app_label": "x", "name": "X",
                 "models": [{"name": "Nascosto", "object_name": "Nascosto"}]}]
    assert build_items(app_list) == []


@pytest.mark.django_db
def test_build_items_honours_exclusions():
    config = {"EXCLUDE_APPS": ["visite"], "EXCLUDE_MODELS": ["pazienti.allegato"]}
    items = build_items(APP_LIST, config={**config, "APP_ICONS": {}, "FALLBACK_ICON": "📄"})
    assert [i["label"] for i in items] == ["Pazienti"]


@pytest.mark.django_db
def test_build_items_returns_plain_strings_for_lazy_names():
    """I nomi dei modelli sono pigri: il menu deve poter finire in JSON."""
    app_list = [{
        "app_label": "lazy",
        "name": _("Pigra"),
        "models": [{"name": _("Cose"), "object_name": "Cosa", "admin_url": "/admin/lazy/cosa/"}],
    }]
    items = build_items(app_list)
    assert type(items[0]["label"]) is str
    assert type(items[0]["app_name"]) is str
    json.dumps(items)   # non deve sollevare eccezioni


@pytest.mark.django_db
def test_build_items_sorted_by_order_then_name():
    MenuIcon.objects.create(app_label="pazienti", model_name="allegato", order=-5)
    items = build_items(APP_LIST)
    assert items[0]["label"] == "Allegati"


@pytest.mark.django_db
def test_tabs_default_to_pinned_entries():
    MenuIcon.objects.create(app_label="visite", model_name="visita", pinned=True)
    tabs = build_tabs(build_items(APP_LIST), home_url="/admin/")
    assert tabs[0]["url"] == "/admin/"
    assert tabs[0]["exact"] is True
    assert [t["label"] for t in tabs[1:]] == ["Visite"]


@pytest.mark.django_db
def test_tabs_fall_back_to_first_items_when_nothing_pinned():
    tabs = build_tabs(build_items(APP_LIST), home_url="/admin/")
    # Home più le prime voci: la barra non resta mai con la sola Home.
    assert len(tabs) > 1


@pytest.mark.django_db
def test_explicit_tabs_win_and_skip_unknown_urls():
    config = {
        "MAX_TABS": 5,
        "TABS": [
            {"url": "/admin/", "label": "Home", "icon": "🏠"},
            {"url_name": "non-esiste", "label": "Fantasma", "icon": "👻"},
            {"url": "/calendario/", "label": "Calendario", "icon": "📅"},
        ],
    }
    tabs = build_tabs(build_items(APP_LIST), config=config, home_url="/admin/")
    assert [t["label"] for t in tabs] == ["Home", "Calendario"]
    # La home va confrontata per intero, le altre per prefisso.
    assert tabs[0].get("exact") is True
    assert "exact" not in tabs[1]


@pytest.mark.django_db
def test_explicit_tabs_respect_max_tabs():
    config = {"MAX_TABS": 2, "TABS": [
        {"url": "/a/", "label": "A"}, {"url": "/b/", "label": "B"}, {"url": "/c/", "label": "C"},
    ]}
    tabs = build_tabs(build_items(APP_LIST), config=config, home_url="/admin/")
    assert len(tabs) == 2


@pytest.mark.django_db
def test_build_menu_shape_is_json_serializable():
    menu = build_menu({"available_apps": APP_LIST, "site_header": _("Amministrazione")})
    payload = json.dumps(menu)
    assert '"groups"' in payload
    assert menu["features"]["tabbar"] is True
    assert {g["app_label"] for g in menu["groups"]} == {"visite", "pazienti"}
    assert menu["urls"]["home"] == "/admin/"


@pytest.mark.django_db
def test_build_menu_reads_app_list_when_available_apps_missing():
    menu = build_menu({"app_list": APP_LIST})
    assert menu["groups"]


@pytest.mark.django_db
def test_config_script_escapes_angle_brackets():
    """Un'etichetta ostile non deve poter chiudere il tag <script>."""
    app_list = [{
        "app_label": "x",
        "name": "</script><script>alert(1)</script>",
        "models": [{"name": "Y", "object_name": "Y", "admin_url": "/admin/x/y/"}],
    }]
    tpl = Template("{% load admin_mobile %}{% mobile_admin_config %}")
    html = tpl.render(Context({"available_apps": app_list}))
    assert "</script><script>" not in html
    assert "\\u003C" in html
