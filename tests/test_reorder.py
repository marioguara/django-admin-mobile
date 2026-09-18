"""Pagina «Organizza il menu»: spostare, nascondere e mettere in evidenza."""

import pytest
from django.contrib.auth.models import Permission, User
from django.urls import reverse

from django_admin_mobile.menu import build_items, build_tabs
from django_admin_mobile.models import MenuIcon


REORDER_URL = "/admin/django_admin_mobile/menuicon/organizza/"


@pytest.fixture
def boss(db):
    return User.objects.create_superuser("capo", "capo@example.com", "x")


@pytest.fixture
def helper(db):
    """Utente di staff senza il permesso di modificare le icone."""
    user = User.objects.create_user("aiuto", "aiuto@example.com", "x", is_staff=True)
    user.user_permissions.add(Permission.objects.get(codename="view_menuicon"))
    return user


def test_url_is_registered():
    assert reverse("admin:django_admin_mobile_menuicon_reorder") == REORDER_URL


@pytest.mark.django_db
def test_page_lists_every_menu_entry_even_without_a_saved_row(client, boss):
    client.force_login(boss)
    response = client.get(REORDER_URL)
    assert response.status_code == 200
    html = response.content.decode()
    # Nessun MenuIcon esiste ancora, ma le voci del menu ci sono lo stesso.
    assert MenuIcon.objects.count() == 0
    assert 'data-key="django_admin_mobile.menuicon"' in html
    assert 'name="entry"' in html
    assert "dam-grip" in html          # maniglia per il trascinamento
    assert 'class="dam-move"' in html  # frecce, per chi non può trascinare


@pytest.mark.django_db
def test_saving_stores_order_icon_and_flags(client, boss):
    client.force_login(boss)
    response = client.post(REORDER_URL, {
        "entry": ["auth.user", "auth.group", "django_admin_mobile.menuicon"],
        "pinned": ["auth.user"],
        "visible": ["auth.user", "django_admin_mobile.menuicon"],
        "icon:auth.user": "🦉",
        "icon:auth.group": "👪",
        "icon:django_admin_mobile.menuicon": "🧩",
    })
    assert response.status_code == 302

    user_icon = MenuIcon.objects.get(app_label="auth", model_name="user")
    assert user_icon.order == 0
    assert user_icon.icon == "🦉"
    assert user_icon.pinned is True
    assert user_icon.visible is True

    group_icon = MenuIcon.objects.get(app_label="auth", model_name="group")
    assert group_icon.order == 1
    # Casella non spuntata: la voce sparisce dal menu.
    assert group_icon.visible is False


@pytest.mark.django_db
def test_saving_twice_updates_the_same_rows(client, boss):
    client.force_login(boss)
    payload = {"entry": ["auth.user"], "visible": ["auth.user"]}
    client.post(REORDER_URL, payload)
    client.post(REORDER_URL, payload)
    assert MenuIcon.objects.filter(app_label="auth", model_name="user").count() == 1


@pytest.mark.django_db
def test_hidden_entries_stay_listed_so_they_can_be_switched_back_on(client, boss):
    MenuIcon.objects.create(app_label="auth", model_name="user", visible=False, icon="🙈")
    client.force_login(boss)
    html = client.get(REORDER_URL).content.decode()
    assert 'data-key="auth.user"' in html
    assert "dam-off" in html


@pytest.mark.django_db
def test_page_is_refused_without_the_change_permission(client, helper):
    client.force_login(helper)
    assert client.get(REORDER_URL).status_code == 403


@pytest.mark.django_db
def test_changelist_offers_the_link(client, boss):
    client.force_login(boss)
    html = client.get("/admin/django_admin_mobile/menuicon/").content.decode()
    assert REORDER_URL in html
    assert "Organizza il menu" in html


# ── Effetto sul menu ──────────────────────────────────────────────────────

APP_LIST = [
    {"app_label": "visite", "name": "Visite", "models": [
        {"name": "Visite", "object_name": "Visita", "admin_url": "/admin/visite/visita/"}]},
    {"app_label": "pazienti", "name": "Pazienti", "models": [
        {"name": "Pazienti", "object_name": "Paziente", "admin_url": "/admin/pazienti/paziente/"}]},
]


@pytest.mark.django_db
def test_pinned_entries_beat_the_tabs_from_settings():
    """Le impostazioni sono il valore di partenza, il pannello la decisione."""
    MenuIcon.objects.create(app_label="pazienti", model_name="paziente", pinned=True)
    config = {"MAX_TABS": 5, "TABS": [
        {"url": "/admin/", "label": "Home"},
        {"url": "/altro/", "label": "Altro"},
    ]}
    tabs = build_tabs(build_items(APP_LIST), config=config, home_url="/admin/")
    assert [t["label"] for t in tabs] == ["Home", "Pazienti"]


@pytest.mark.django_db
def test_hidden_entry_disappears_from_the_menu():
    MenuIcon.objects.create(app_label="visite", model_name="visita", visible=False)
    labels = [i["label"] for i in build_items(APP_LIST)]
    assert "Visite" not in labels
    assert "Pazienti" in labels


@pytest.mark.django_db
def test_order_saved_from_the_page_drives_the_menu():
    MenuIcon.objects.create(app_label="pazienti", model_name="paziente", order=0)
    MenuIcon.objects.create(app_label="visite", model_name="visita", order=1)
    assert [i["label"] for i in build_items(APP_LIST)] == ["Pazienti", "Visite"]
