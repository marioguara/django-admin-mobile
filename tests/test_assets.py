"""Guardie sul foglio di stile.

Sono controlli su del testo, non su del comportamento: servono a non
ri-inciampare in sovrascritture di Django che si notano solo guardando la
pagina su un telefono.
"""

from pathlib import Path

import pytest

import django_admin_mobile


STATIC = Path(django_admin_mobile.__file__).parent / "static" / "django_admin_mobile"
CSS = (STATIC / "css" / "admin_mobile.css").read_text(encoding="utf-8")
JS = (STATIC / "js" / "admin_mobile.js").read_text(encoding="utf-8")


def _rule(selector):
    """Il corpo della prima regola che comincia con questo selettore."""
    start = CSS.index(selector)
    return CSS[start:CSS.index("}", start)]


def test_submit_row_declares_its_direction():
    """`responsive.css` di Django impone `flex-direction: column` alla
    submit-row sotto i 767 px. Senza dichiarare la direzione, i bottoni
    restano incolonnati e la barra copre mezzo modulo."""
    rule = _rule("body.dam-mobile.dam-forms .submit-row {")
    assert "flex-direction: row" in rule
    assert "flex-wrap: nowrap" in rule


def test_form_content_reserves_the_measured_bar_height():
    """Un valore fisso sbaglia: la barra cambia con lingua, bottoni e tacca."""
    rule = _rule("body.dam-mobile.dam-forms.dam-has-submitrow #content {")
    assert "var(--dam-submitrow-h" in rule
    assert "--dam-submitrow-h" in JS, "l'altezza dev'essere misurata dal JavaScript"


def test_editing_replaces_the_tab_bar():
    """Due barre fisse in fondo rubano troppo schermo mentre si compila."""
    assert "body.dam-mobile.dam-editing .dam-tabbar { display: none; }" in CSS


def test_collapsed_fieldsets_stay_collapsed():
    """`fieldset.collapsed * {display:none}` di Django è meno specifico
    delle regole del pacchetto: serve una regola esplicita."""
    assert "fieldset.collapsed .form-row" in CSS


@pytest.mark.parametrize("token", [
    "--dam-safe-bottom",
    "env(safe-area-inset-bottom",
])
def test_bars_respect_the_phone_safe_area(token):
    assert token in CSS
