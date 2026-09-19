# Changelog

Tutte le modifiche degne di nota vengono documentate qui.
Il formato segue [Keep a Changelog](https://keepachangelog.com/it/1.1.0/)
e il progetto usa [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.3.3] - 2026-09-19

### Modificato
- **Gli strumenti dell'oggetto** («Storia», «Vedi sul sito», le azioni che il
  progetto aggiunge di suo) su telefono diventano chip leggeri: bordo invece
  di riempimento, scritti in tondo a 14 px, alti 44 px. Django li rende come
  pillole piene alte 26 px con testo di 11 px tutto maiuscolo — pesanti da
  vedere e troppo piccole da centrare col dito.

### Corretto
- **Negli elenchi spariva tutto il gruppo strumenti**, non solo il «+»
  sostituito dal bottone flottante: gli strumenti aggiunti dal progetto
  diventavano irraggiungibili. Ora si nasconde solo la voce sostituita, e il
  gruppo scompare soltanto se resta vuoto.

## [0.3.2] - 2026-09-19

Rilievi emersi passando in rassegna 92 schermate dell'admin a 320 e 360 px.

### Corretto
- **L'ultima riga del contenuto restava sotto le barre fisse.** L'admin dà a
  `html`, `body` e `#container` `height: 100%`: un contenuto più lungo della
  finestra li sfora, e lo spazio riservato in fondo al body non finiva mai
  sotto al contenuto vero. Su telefono il documento può ora crescere.
- **I bottoni delle pagine di conferma** (eliminazione singola e di massa)
  finivano sotto le barre: quelle pagine non usano `.submit-row`, i comandi
  stanno in un `<div>` qualsiasi. Ora vengono riconosciuti e trattati come
  barra delle azioni, con la stessa resa.
- **L'invito a installare copriva il bottone flottante** «Aggiungi»: la sua
  altezza viene ora misurata e lo spazio riservato, come per la barra azioni.
- **Il bottone flottante copriva il «Salva»** negli elenchi modificabili in
  linea: ora si posiziona sopra la barra di salvataggio.

### Aggiunto
- Guardie nei test sul foglio di stile e sullo script, per non ri-inciampare
  nelle sovrascritture di Django che si vedono solo su un telefono.

## [0.3.1] - 2026-09-18

### Modificato
- **La barra delle azioni dei moduli è ora una riga sola.** Resta in vista
  l'azione principale (quella che Django marca come predefinita, altrimenti
  «Salva», altrimenti «Salva e continua»); le altre — compresa l'eliminazione,
  in fondo e in rosso — stanno dietro il tasto «⋯», in un pannello che sale
  dal basso. Con tre o quattro bottoni a tutta larghezza la barra copriva metà
  del modulo.
  I bottoni spostati restano bottoni veri: escono dal `<form>` ma vengono
  riagganciati con l'attributo `form=`, così continuano a inviare il proprio
  `name` (`_continue`, `_addanother`…). Se il modulo non ha un `id` non si
  sposta niente e la riga scorre in orizzontale.
- **Mentre si compila un modulo la barra prende il posto della barra di
  navigazione**: due barre fisse una sopra l'altra rubavano 120 px di schermo.
  Si esce con il tasto indietro in alto; il menu resta sotto la lente.

### Corretto
- **La barra restava alta il doppio del necessario** (122 px invece di 66):
  `responsive.css` di Django impone `flex-direction: column` alla submit-row
  sotto i 767 px, e il pacchetto non dichiarava la direzione.
- Lo spazio riservato in fondo al contenuto non era più un valore fisso di
  82 px ma l'altezza vera della barra, misurata dal JavaScript e aggiornata
  a ogni ridimensionamento: nessun campo resta più coperto.

## [0.3.0] - 2026-09-18

### Aggiunto
- **Installazione come app.** Includendo `django_admin_mobile.urls` il
  pacchetto serve manifest, service worker, un'icona di ripiego e una pagina
  di cortesia per quando manca la rete; nel `<head>` finiscono il collegamento
  al manifest e le indicazioni per iOS. Su Android compare un invito a
  installare in fondo allo schermo, su iPhone la voce «Installa l'app» nel
  menu laterale spiega come fare. Undici nuove chiavi `PWA_*`.
  Il service worker è servito da una vista proprio per poter mandare
  `Service-Worker-Allowed`: da `/static/` non potrebbe governare `/admin/`.
  Strategia: sempre la rete, la cache solo quando la rete manca.
- **Pagina «Organizza il menu»** (*Icone menu mobile → Organizza il menu*):
  si spostano le voci trascinandole per la maniglia o con le frecce su/giù, si
  cambia l'icona, si nasconde una voce e si sceglie cosa mettere nella barra
  in basso. Il trascinamento usa i Pointer Events, quindi funziona col dito;
  le frecce restano per chi usa la tastiera. L'elenco mostra anche le voci
  che non hanno ancora una configurazione salvata.
- `build_items(..., include_hidden=True)` e campo `visible` nelle voci.

### Modificato
- La barra in basso segue ora questo ordine: voci «in evidenza» scelte dal
  pannello, poi `TABS` dei settings, poi le prime voci. Le impostazioni
  restano il valore di partenza, la scelta fatta dal pannello vince.
- Il titolo nella barra in alto usa l'intestazione della pagina quando c'è
  (prima una pagina secondaria mostrava il nome della sezione).

### Corretto
- **`visible = False` ora nasconde davvero la voce.** Le configurazioni
  venivano caricate filtrando `visible=True`: la voce nascosta non trovava
  configurazione e ricadeva sui valori di default, restando visibile.
- L'invito a installare non compare più sulle pagine con la barra di
  salvataggio fissa, che copriva.

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
