# django-admin-mobile

Griglia mobile con **icone configurabili** e CSS responsive per il pannello
`django.contrib.admin`. Trasforma il classico elenco di app/modelli in una
tavolozza di bottoni comodi da toccare su smartphone e tablet.

- Nuova sezione admin per configurare icona, colore e ordinamento di ogni
  app/modello, senza toccare il codice.
- Fallback automatico su emoji predefinite quando l'icona non è configurata.
- CSS "drop-in": bottoni tattili, form leggibili, changelist a card, drawer
  filtri.
- Zero dipendenze oltre Django. Compatibile con Django 3.2 → 5.x.

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

## Utilizzo

Nessuna configurazione obbligatoria: aprendo `/admin/` da mobile vedrai
subito la griglia di bottoni. Da desktop il layout classico rimane
invariato.

### Configurare le icone

1. Vai in `Admin Mobile → Icone menu mobile`.
2. Crea una `MenuIcon` scegliendo:
   - **App label** (es. `pazienti`) — obbligatorio.
   - **Model name** (es. `paziente`) — vuoto per icona a livello app.
   - **Icon** — emoji o carattere unicode (es. `📅`).
   - **Color / background** — colori esadecimali.
   - **Order / visible** — controllano ordinamento e visibilità.

### Uso manuale del template tag

Se vuoi mostrare la griglia in un tuo template (dashboard custom):

```django
{% load admin_mobile %}
{% render_mobile_menu app_list %}
```

Per caricare CSS/JS in un tuo template `admin/base.html`:

```django
{% load admin_mobile %}
{% block extrastyle %}{{ block.super }}{% mobile_admin_assets %}{% endblock %}
```

### CSS incluso

Il file `django_admin_mobile/css/admin_mobile.css` applica sotto i 1024px:

- Griglia menu (`.dam-mobile-menu` / `.dam-tile`).
- Form con `min-height: 44px` e `font-size: 16px` (no zoom iOS).
- `submit-row` sticky in basso.
- Changelist come card impilate quando `body.dam-cards` è attivo.
- Drawer laterale per i filtri con FAB "⚙ Filtri".
- Tab bar opzionale `.dam-tabbar`.
- Compatibilità tema scuro admin (`html[data-theme="dark"]`).

## Sviluppo

```bash
git clone https://github.com/your-org/django-admin-mobile
cd django-admin-mobile
pip install -e ".[dev]"
pytest
```

## Compatibilità

| Django | Python |
| :---: | :---: |
| 3.2 | 3.9 – 3.10 |
| 4.2 | 3.9 – 3.12 |
| 5.0 | 3.10 – 3.12 |
| 5.1 | 3.10 – 3.12 |

## Licenza

MIT — vedi [LICENSE](LICENSE).
