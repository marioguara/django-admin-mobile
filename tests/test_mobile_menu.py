import pytest
from django.core.exceptions import ValidationError
from django.template import Context, Template

from django_admin_mobile.models import MenuIcon


APP_LIST_FIXTURE = [
    {
        "app_label": "pazienti",
        "name": "Pazienti",
        "models": [
            {
                "name": "Pazienti",
                "object_name": "Paziente",
                "admin_url": "/admin/pazienti/paziente/",
            },
        ],
    },
    {
        "app_label": "custom_app",
        "name": "Custom",
        "models": [
            {
                "name": "Widget",
                "object_name": "Widget",
                "admin_url": "/admin/custom_app/widget/",
            },
        ],
    },
]


@pytest.mark.django_db
def test_menu_icon_str_and_uniqueness():
    icon = MenuIcon.objects.create(app_label="pazienti", model_name="paziente", icon="🧑‍⚕️")
    assert "pazienti.paziente" in str(icon)
    assert icon.is_app_level is False

    app_icon = MenuIcon.objects.create(app_label="pazienti", icon="🏥")
    assert app_icon.is_app_level is True


@pytest.mark.django_db
def test_menu_icon_hex_validation():
    icon = MenuIcon(app_label="a", color="not-a-color")
    with pytest.raises(ValidationError):
        icon.full_clean()


def _render(app_list):
    tpl = Template("{% load admin_mobile %}{% render_mobile_menu app_list %}")
    return tpl.render(Context({"app_list": app_list}))


@pytest.mark.django_db
def test_render_mobile_menu_uses_defaults_when_no_config():
    html = _render(APP_LIST_FIXTURE)
    # Icona di default per pazienti presa dalla mappa DEFAULT_APP_ICONS.
    assert "🧑‍⚕️" in html or "🧑‍⚕️" in html
    # Icona di default generica per una app non nota.
    assert "📄" in html
    assert "/admin/pazienti/paziente/" in html


@pytest.mark.django_db
def test_render_mobile_menu_applies_model_config():
    MenuIcon.objects.create(
        app_label="pazienti",
        model_name="paziente",
        icon="🩺",
        color="#123456",
        background="#abcdef",
        label_override="Cartelle",
        order=5,
    )
    html = _render(APP_LIST_FIXTURE)
    assert "🩺" in html
    assert "#123456" in html
    assert "#abcdef" in html
    assert "Cartelle" in html


@pytest.mark.django_db
def test_render_mobile_menu_falls_back_to_app_level_config():
    MenuIcon.objects.create(app_label="custom_app", icon="🎯", color="#000000")
    html = _render(APP_LIST_FIXTURE)
    assert "🎯" in html


@pytest.mark.django_db
def test_render_mobile_menu_respects_visible_flag():
    MenuIcon.objects.create(
        app_label="pazienti",
        model_name="paziente",
        icon="🚫",
        visible=False,
    )
    html = _render(APP_LIST_FIXTURE)
    # L'icona non visibile viene ignorata: torna all'icona di default.
    assert "🚫" not in html


def test_render_mobile_menu_empty_app_list_renders_nothing():
    html = _render([])
    assert "dam-mobile-menu" not in html


def test_mobile_admin_assets_outputs_link_and_script():
    tpl = Template("{% load admin_mobile %}{% mobile_admin_assets %}")
    html = tpl.render(Context({}))
    assert "admin_mobile.css" in html
    assert "admin_mobile.js" in html
