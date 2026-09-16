# Changelog

Tutte le modifiche degne di nota vengono documentate qui.
Il formato segue [Keep a Changelog](https://keepachangelog.com/it/1.1.0/)
e il progetto usa [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-09-17

### Aggiunto
- Modello `MenuIcon` per configurare icona / colore / ordinamento per app o
  modello dal pannello admin.
- Template `admin/index.html` con griglia mobile di bottoni sopra al
  layout classico.
- Template tag `{% render_mobile_menu app_list %}` e
  `{% mobile_admin_assets %}`.
- Foglio di stile `admin_mobile.css` con:
  griglia bottoni, form touch-friendly, changelist a card, drawer filtri,
  supporto tema scuro admin.
- Script `admin_mobile.js` per trasformare la tabella changelist in card
  e per aprire il drawer dei filtri.
- Migrazione iniziale `0001_initial`.
