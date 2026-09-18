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
| **Moduli** | campi a tutta larghezza, barra di salvataggio fissa in fondo, nessun campo che sfonda lo schermo |

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

Se invece il progetto sovrascrive `admin/base.html` (o vuoi la shell anche
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

### Barra in basso

Senza `TABS` la barra si costruisce da sola: *Home*, le voci marcate **In
evidenza** nelle icone del menu (o le prime dell'elenco, se non ne hai
marcata nessuna) e *Menu*.

Con `TABS` decidi tu, e puoi puntare a qualunque URL del progetto, non solo a
pagine dell'admin:

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

La sezione **Admin Mobile → Icone menu mobile** permette al cliente di
cambiare icona, colori, nome, ordine e visibilità di ogni voce senza toccare
il codice, e di marcare le voci **In evidenza** che finiscono nella barra in
basso.

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
- **Il tema** usa le stesse chiavi di `theme.js` di Django, quindi la scelta
  fatta dal menu laterale vale anche da computer.

## Sviluppo

```bash
pip install -e ".[dev]"
pytest
```

## Licenza

MIT.
