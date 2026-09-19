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
    """Un valore fisso sbaglia: la barra cambia con lingua, bottoni e tacca.

    Lo spazio si riserva sul body, non sul solo #content: quello che il
    progetto aggiunge dopo il contenuto finirebbe sotto le barre."""
    rule = _rule("body.dam-mobile.dam-has-submitrow {")
    assert "var(--dam-submitrow-h" in rule
    assert "--dam-submitrow-h" in JS, "l'altezza dev'essere misurata dal JavaScript"


def test_editing_replaces_the_tab_bar():
    """Due barre fisse in fondo rubano troppo schermo mentre si compila."""
    assert "body.dam-mobile.dam-editing .dam-tabbar { display: none; }" in CSS


def test_collapsed_fieldsets_stay_collapsed():
    """`fieldset.collapsed * {display:none}` di Django è meno specifico
    delle regole del pacchetto: serve una regola esplicita."""
    assert "fieldset.collapsed .form-row" in CSS


def test_mobile_lets_the_document_grow():
    """L'admin dà a html, body e #container `height: 100%`: il contenuto più
    lungo della finestra li sfora e lo spazio riservato in fondo al body non
    finirebbe mai sotto al contenuto vero, lasciando l'ultima riga coperta."""
    rule = _rule("body.dam-mobile #container {")
    assert "height: auto" in rule
    assert "min-height: 100%" in rule


def test_confirmation_pages_get_an_action_bar():
    """Le pagine di conferma di Django non usano .submit-row: i bottoni
    starebbero in fondo alla pagina, sotto le barre fisse."""
    assert "adoptConfirmRow" in JS
    assert 'classList.add("submit-row", "dam-synth-row")' in JS
    # ...ma negli elenchi il primo invio è il bottone "Cerca", non una conferma.
    assert 'if (KIND === "changelist") { return null; }' in JS


def test_object_tools_are_big_enough_to_tap():
    """Django li rende alti 26 px con testo di 11 px tutto maiuscolo:
    pesanti da vedere e troppo piccoli da centrare col dito."""
    rule = _rule("body.dam-mobile .object-tools a,")
    assert "min-height: 44px" in rule
    assert "text-transform: none" in rule


def test_only_the_replaced_add_link_is_hidden():
    """Nascondere tutto il gruppo renderebbe irraggiungibili gli strumenti
    che il progetto aggiunge di suo accanto al «+»."""
    assert "body.dam-mobile .object-tools li.dam-hidden-tool" in CSS
    assert 'classList.add("dam-hidden-tool")' in JS
    assert "dam-empty-tools" in JS


@pytest.mark.parametrize("token", [
    "--dam-safe-bottom",
    "env(safe-area-inset-bottom",
])
def test_bars_respect_the_phone_safe_area(token):
    assert token in CSS
