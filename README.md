# django-admin-mobile

L'admin di Django con l'aspetto e i gesti di una normale app per telefono,
senza toccare i template del progetto.

Su schermi piccoli il pacchetto costruisce una vera shell applicativa sopra
l'admin esistente:

| | |
|---|---|
| **Barra in alto** | titolo della sezione, tasto indietro contestuale, ricerca |
| **Barra in basso** | le destinazioni principali, con lo stato attivo |
| **Menu laterale** | tutte le sezioni raggruppate per app, con ricerca istantanea, scorciatoie "+ aggiungi", cambio tema e uscita |
| **Schermata home** | le sezioni come icone, in stile schermata di un telefono |
| **Elenchi** | righe a schede con etichette di colonna, riga toccabile, ricerca sempre visibile, filtri in un pannello che sale dal basso, bottone flottante per aggiungere |
| **Azioni di massa** | nascoste finché non selezioni delle righe, poi salgono dal basso |
| **Moduli** | campi a tutta larghezza, una sola riga di azioni in fondo (le secondarie dietro «⋯»), nessun campo coperto né sfondato |
| **Installazione** | l'admin si aggiunge alla schermata iniziale e si apre a tutto schermo, come un'app |
| **Menu modificabile** | chi usa il gestionale sposta le voci trascinandole, cambia le icone e sceglie cosa mettere nella barra in basso |

Da computer non cambia nulla: l'admin resta quello di Django.

- Zero dipendenze oltre Django. Compatibile con Django 3.2 → 5.x.
- Nessuna modifica ai template del progetto: basta un tag.
- Il menu si costruisce da `available_apps`, quindi rispetta già i permessi.

## Installazione

```bash
pip install django-admin-mobile
```

Aggiungi l'app a `INSTALLED_APPS` **prima** di `django.contrib.admin` (serve
per far vincere il template `admin/index.html` fornito dal pacchetto):

```python
INSTALLED_APPS = [
    "django_admin_mobile",
    "django.contrib.admin",
    # ...
]
```

Esegui la migrazione:

```bash
python manage.py migrate django_admin_mobile
```

## Attivazione

Se il progetto **non** ha un suo `templates/admin/base.html`, non serve altro:
il template `admin/index.html` del pacchetto include già tutto.

Per rendere l'admin installabile come app, includi anche gli URL del
pacchetto (facoltativo: senza, tutto il resto funziona lo stesso):

```python
urlpatterns = [
    path("admin/", admin.site.urls),
    path("admin-mobile/", include("django_admin_mobile.urls")),
]
```

Se il progetto sovrascrive `admin/base.html` (o vuoi la shell anche
sulle pagine che non passano dall'index), aggiungi una riga nel `<head>`:

```django
{% load admin_mobile %}
...
{% mobile_admin_assets %}
```

Quel tag pubblica il foglio di stile, i dati del menu (in un
`<script type="application/json">`) e lo script che costruisce la shell.

## Configurazione

Tutto si regola da un unico dizionario nei settings. Ogni chiave è
facoltativa:

```python
ADMIN_MOBILE = {
    # Aspetto
    "ACCENT": "#417690",        # colore delle barre e degli stati attivi
    "TITLE": None,              # titolo in alto; None = site_header dell'admin
    "BREAKPOINT": 1024,         # sotto questa larghezza si attiva la shell

    # Barra in basso
    "MAX_TABS": 5,
    "TABS": [],                 # vedi sotto

    # Cosa mostrare nel menu
    "EXCLUDE_APPS": [],         # ["sessions"]
    "EXCLUDE_MODELS": [],       # ["auth.permission"]
    "APP_ICONS": {},            # {"fatture": "🧾"}
    "FALLBACK_ICON": "📄",

    # Installazione come app
    "PWA": True,
    "PWA_PROMPT": True,          # invito a installare, su telefono
    "PWA_NAME": None,            # None = TITLE
    "PWA_SHORT_NAME": None,      # None = le prime parole del nome
    "PWA_DESCRIPTION": "",
    "PWA_ICONS": [],             # vedi sotto
    "PWA_START_URL": None,       # None = pagina iniziale dell'admin
    "PWA_SCOPE": None,
    "PWA_DISPLAY": "standalone",
    "PWA_ORIENTATION": "portrait",
    "PWA_BACKGROUND": "#ffffff",
    "PWA_CACHE_VERSION": "1",    # cambialo per svuotare la cache

    # Componenti: si spengono uno per uno
    "APPBAR": True,
    "TABBAR": True,
    "DRAWER": True,
    "CARDS": True,              # elenchi a schede
    "FILTER_SHEET": True,       # filtri nel pannello dal basso
    "FAB": True,                # bottone flottante "aggiungi"
    "FORMS": True,              # adattamento dei campi
    "HIDE_DJANGO_CHROME": True, # nasconde header, briciole e sidebar su telefono
}
```

### Installazione come app

Con gli URL inclusi il pacchetto serve da solo il manifest, il service worker
e una pagina di cortesia per quando manca la rete. Su Android compare un
invito a installare in fondo allo schermo; su iPhone la voce **Installa
l'app** nel menu laterale spiega come fare dal tasto Condividi. In entrambi i
casi la voce resta nel menu laterale anche dopo aver chiuso l'invito.

Il service worker è servito da una vista, non da `/static/`: solo così può
mandare l'intestazione `Service-Worker-Allowed` e governare le pagine
dell'admin. Usa **sempre la rete** e la cache solo quando la rete manca: in un
gestionale un dato vecchio fa più danno di un caricamento lento.

Le icone: senza `PWA_ICONS` il pacchetto ne genera una con il colore dell'app
e l'iniziale del nome, utile per partire. Per un risultato curato dichiara dei
PNG veri:

```python
ADMIN_MOBILE = {
    "PWA_ICONS": [
        {"src": "img/app-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "img/app-192.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable"},
        {"src": "img/app-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
    ],
}
```

`src` accetta sia un percorso statico sia un indirizzo completo. Ricorda che i
browser propongono l'installazione solo su HTTPS (in sviluppo vale anche
`localhost`).

### Organizza il menu, senza toccare il codice

*Admin Mobile → Icone menu mobile → **Organizza il menu*** apre una pagina
dove chi usa il gestionale può, da solo:

- **spostare** le voci trascinandole per la maniglia (funziona col dito,
  perché usa i Pointer Events e non il drag-and-drop HTML5) oppure con le
  frecce su/giù, che restano l'unica via da tastiera;
- **cambiare l'icona** scrivendo un'altra emoji;
- **nascondere** una voce dal menu;
- metterla **In evidenza**, cioè nella barra in basso.

L'elenco mostra tutte le voci del menu, comprese quelle che non hanno ancora
una configurazione salvata: il record viene creato al primo salvataggio.

### Barra in basso

Ordine di precedenza:

1. le voci marcate **In evidenza** dalla pagina qui sopra;
2. `TABS` nei settings;
3. le prime voci del menu, così la barra non è mai vuota.

In pratica: `TABS` è il valore di partenza che decidi tu, e resta valido
finché nessuno sceglie qualcosa dal pannello.

Con `TABS` puoi puntare a qualunque URL del progetto, non solo a pagine
dell'admin:

```python
ADMIN_MOBILE = {
    "TABS": [
        {"url_name": "admin:index", "label": "Home", "icon": "🏠"},
        {"url_name": "admin:ordini_ordine_changelist", "label": "Ordini", "icon": "📦"},
        {"url_name": "report:dashboard", "label": "Report", "icon": "📈"},
        {"url": "/magazzino/", "label": "Magazzino", "icon": "🏷️"},
    ],
}
```

Una voce il cui indirizzo non esiste viene semplicemente saltata: la barra non
si rompe se rimuovi un'app. La voce attiva è quella il cui indirizzo è il
prefisso più lungo dell'indirizzo corrente (la home si confronta per intero).

### Icone, dal pannello admin

La sezione **Admin Mobile → Icone menu mobile** è la vista completa, con
anche i colori e il nome da mostrare. Per il solo riordino conviene la pagina
*Organizza il menu* descritta sopra.

Ordine con cui si sceglie l'icona di una voce:

1. `MenuIcon` per quel modello (`app_label` + `model_name`)
2. `MenuIcon` per l'app (`app_label`, `model_name` vuoto)
3. `ADMIN_MOBILE["APP_ICONS"][app_label]`
4. icone predefinite del pacchetto
5. `ADMIN_MOBILE["FALLBACK_ICON"]`

Se la tabella non è ancora migrata il pacchetto usa i default senza errori.

## Tag disponibili

| Tag | A cosa serve |
|---|---|
| `{% mobile_admin_assets %}` | CSS + dati del menu + JavaScript. È l'unico necessario. |
| `{% mobile_admin_config %}` | Solo i dati del menu, per chi vuole posizionarli a mano. |
| `{% render_mobile_menu app_list %}` | La griglia di icone, per metterla in una pagina propria. |

## Note di funzionamento

- **Il menu è costruito dal server** e consegnato al browser in JSON: niente
  viene indovinato leggendo il DOM, e i permessi dell'utente sono già
  applicati da `available_apps`.
- **Gli spostamenti nel DOM sono reversibili**: ricerca e filtri vengono
  spostati nella shell quando si passa a telefono e rimessi al loro posto se
  la finestra torna larga, così ruotare lo schermo non rompe la pagina.
- **Le azioni di massa restano dentro `#changelist-form`**, perché il
  JavaScript di Django le cerca lì: vengono solo nascoste finché non
  selezioni qualcosa.
- **Le finestre pop-up** (selettore di chiave esterna) e la **pagina di
  accesso** non ricevono la shell.
- **L'invito a installare** non compare sulle pagine con la barra di
  salvataggio fissa, per non coprirla.
- **Le azioni secondarie di un modulo** escono dal `<form>` ma restano
  agganciate con l'attributo `form=`: continuano a inviare il proprio `name`.
  Se il modulo non ha un `id` non viene spostato niente.
- **Mentre si compila un modulo** la barra delle azioni prende il posto della
  barra di navigazione: lo spazio in fondo allo schermo è poco.
- **Il tema** usa le stesse chiavi di `theme.js` di Django, quindi la scelta
  fatta dal menu laterale vale anche da computer.

## Sviluppo

```bash
pip install -e ".[dev]"
pytest
```

## Licenza

MIT.
