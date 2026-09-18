# Changelog

Tutte le modifiche degne di nota vengono documentate qui.
Il formato segue [Keep a Changelog](https://keepachangelog.com/it/1.1.0/)
e il progetto usa [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.2.0] - 2026-09-18

Il pacchetto non è più solo una griglia di icone: su telefono costruisce una
vera shell applicativa sopra l'admin esistente.

### Aggiunto
- **Barra in alto** con titolo della sezione, tasto indietro contestuale e
  scorciatoia di ricerca.
- **Barra di navigazione in basso**, con voce attiva calcolata sull'indirizzo
  corrente. Si configura da `ADMIN_MOBILE["TABS"]` (anche verso URL fuori
  dall'admin) oppure marcando le voci "In evidenza".
- **Menu laterale** con ricerca istantanea fra tutte le sezioni, scorciatoie
  "+ aggiungi", collegamenti al sito e al cambio password, selettore del tema
  e uscita.
- **Pannello dal basso per i filtri** degli elenchi, con contatore dei filtri
  attivi.
- **Bottone flottante** per aggiungere un elemento dagli elenchi.
- **Azioni di massa** nascoste finché non si seleziona una riga, poi mostrate
  come barra in fondo allo schermo.
- Righe degli elenchi toccabili per intero, con etichette di colonna e freccia.
- Schermata home a icone anche nei progetti che hanno una dashboard propria.
- Modulo di configurazione `ADMIN_MOBILE` con dodici chiavi (colore, soglia,
  esclusioni, icone per app, accensione dei singoli componenti).
- `MenuIcon.pinned` ("In evidenza") per portare una voce nella barra in basso.
- Copertura CSS di tutti i widget dell'admin (data e ora, chiave esterna,
  molti-a-molti, file, sola lettura, gruppi di opzioni) e degli editor di terze
  parti (CKEditor, Summernote, TinyMCE), più i filtri per intervallo di date.
- Tag `{% mobile_admin_config %}` e modulo `django_admin_mobile.menu` con
  `build_items`, `build_groups`, `build_tabs`, `build_menu`.
- Migrazione `0002_menuicon_pinned`.

### Modificato
- Il menu ora si costruisce **lato server** da `available_apps` e viaggia verso
  il browser in JSON: i permessi sono rispettati e il JavaScript non deve più
  indovinare niente leggendo il DOM.
- Lo stile per telefono è tutto sotto `body.dam-mobile`, classe messa dal
  JavaScript in base a `BREAKPOINT`: la soglia è davvero configurabile.
- Gli spostamenti nel DOM sono reversibili: allargando la finestra ricerca e
  filtri tornano al loro posto.
- `{% mobile_admin_assets %}` accetta il context (serve per costruire il menu);
  la chiamata nei template resta identica.
- `{% render_mobile_menu %}` raggruppa le icone per applicazione.

### Corretto
- I nomi dei modelli sono stringhe di traduzione pigre: ora vengono convertite,
  altrimenti il menu non era serializzabile in JSON.
- La barra degli strumenti degli elenchi viene inserita accanto a
  `#changelist-form` e non dentro `#changelist`: da Django 4.1 il form sta
  dentro `.changelist-form-container`.
- I fieldset richiudibili restano chiusi (la regola di Django era meno
  specifica di quella del pacchetto e le righe riapparivano come strisce vuote).
- Il link "Mostra/Nascondi" di un fieldset eredita il colore dell'intestazione.
- L'elenco non viene più incorniciato: `#changelist` porta la classe `module`
  ma non deve diventare una scheda.

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
