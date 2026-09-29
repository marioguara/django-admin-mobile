from django.core.validators import RegexValidator
from django.db import models


HEX_COLOR_VALIDATOR = RegexValidator(
    regex=r"^#(?:[0-9a-fA-F]{3}){1,2}$",
    message="Il colore deve essere in formato esadecimale, es. #417690.",
)


class MenuGroup(models.Model):
    """Una sezione del menu, con un nome scelto da chi lo usa.

    Senza, le sezioni sono le app di Django: nomi che significano qualcosa per
    chi ha scritto il codice e niente per chi lo usa, e soprattutto confini
    sbagliati. «Come esce il referto» sta in due app diverse; «cosa devo fare
    oggi» in tre. Un gruppo può raccogliere modelli di **app diverse**, così il
    menu segue le domande di chi lavora invece della struttura del progetto.

    Le voci senza gruppo restano raggruppate per app, come prima: chi non
    configura niente non si accorge che questo modello esiste.
    """

    nome = models.CharField(
        max_length=80,
        verbose_name="Nome della sezione",
        help_text="Come si chiama nel menu, es. «Oggi in studio».",
    )
    icona = models.CharField(
        max_length=16,
        blank=True,
        default="",
        verbose_name="Icona",
        help_text="Facoltativa: compare accanto al nome della sezione.",
    )
    ordine = models.IntegerField(
        default=0,
        verbose_name="Ordine",
        help_text="Le sezioni si susseguono da questo numero, dal più piccolo.",
    )
    visibile = models.BooleanField(
        default=True,
        verbose_name="Visibile",
        help_text="Togli la spunta per nascondere la sezione e tutte le sue voci.",
    )

    class Meta:
        verbose_name = "Sezione del menu"
        verbose_name_plural = "Sezioni del menu"
        ordering = ("ordine", "nome")

    def __str__(self):
        return f"{self.icona} {self.nome}".strip()


class MenuIconQuerySet(models.QuerySet):
    def as_map(self):
        """Restituisce {(app_label, model_name_minuscolo_o_vuoto): MenuIcon}."""
        return {(mi.app_label, mi.model_name.lower()): mi for mi in self}


class MenuIcon(models.Model):
    """Icona di un'app o di un modello nel menu: la stessa su telefono e su schermo grande."""

    app_label = models.CharField(
        max_length=100,
        verbose_name="App",
        help_text="Etichetta dell'app Django (es. `pazienti`, `visite`, `auth`).",
    )
    model_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Modello",
        help_text=(
            "Nome del modello in minuscolo (es. `paziente`). "
            "Lascia vuoto per assegnare l'icona all'intera app."
        ),
    )
    icon = models.CharField(
        max_length=16,
        default="📋",
        verbose_name="Icona",
        help_text="Emoji o carattere unicode da mostrare come icona del bottone.",
    )
    color = models.CharField(
        max_length=7,
        default="#417690",
        verbose_name="Colore",
        validators=[HEX_COLOR_VALIDATOR],
        help_text="Colore del testo / bordo (formato #RRGGBB).",
    )
    background = models.CharField(
        max_length=7,
        default="#ffffff",
        verbose_name="Sfondo",
        validators=[HEX_COLOR_VALIDATOR],
        help_text="Colore di sfondo del bottone (formato #RRGGBB).",
    )
    label_override = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nome mostrato",
        help_text="Se valorizzato, sovrascrive il nome mostrato sul bottone.",
    )
    order = models.IntegerField(
        default=0,
        verbose_name="Ordine",
        help_text="Ordinamento crescente all'interno del menu.",
    )
    visible = models.BooleanField(
        default=True,
        verbose_name="Visibile",
        help_text="Se disattivato, la voce non compare nel menu.",
    )
    gruppo = models.ForeignKey(
        MenuGroup,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="voci",
        verbose_name="Sezione",
        help_text="Lascia vuoto per tenere la voce nella sezione della sua app.",
    )
    pinned = models.BooleanField(
        default=False,
        verbose_name="In evidenza",
        help_text=(
            "Se attivo, la voce compare anche nella barra di navigazione in "
            "basso, come in una normale app per telefono."
        ),
    )

    objects = MenuIconQuerySet.as_manager()

    class Meta:
        verbose_name = "Icona del menu"
        verbose_name_plural = "Icone del menu"
        ordering = ("order", "app_label", "model_name")
        unique_together = (("app_label", "model_name"),)

    def __str__(self):
        target = self.app_label
        if self.model_name:
            target = f"{self.app_label}.{self.model_name}"
        return f"{self.icon} {target}"

    @property
    def is_app_level(self):
        return not self.model_name

    @classmethod
    def sincronizza(cls, site=None):
        """Crea le voci mancanti per ogni modello registrato nell'admin.

        Prima queste righe andavano create a mano, scrivendo `app_label` e
        `model_name` esatti: un modello registrato dopo non compariva
        nell'elenco, quindi la sua icona non si poteva cambiare pur vedendola
        nel menu. Ora l'elenco si riempie da sé e all'utente resta solo da
        ritoccare icona, nome e ordine.

        Restituisce quante voci ha aggiunto.
        """
        from django.contrib import admin as django_admin

        from .conf import get_config
        from .menu import _icon_for

        site = site or django_admin.site
        config = get_config()
        app_escluse = set(config.get("EXCLUDE_APPS") or [])
        modelli_esclusi = {m.lower() for m in (config.get("EXCLUDE_MODELS") or [])}

        esistenti = set(cls.objects.values_list("app_label", "model_name"))
        nuove = []
        for modello in site._registry:
            app_label = modello._meta.app_label
            model_name = modello._meta.model_name
            if app_label in app_escluse:
                continue
            if f"{app_label}.{model_name}" in modelli_esclusi:
                continue
            if (app_label, model_name) in esistenti:
                continue
            nuove.append(cls(
                app_label=app_label,
                model_name=model_name,
                # La stessa icona che il menu mostrerebbe da sé: così la voce
                # nasce già com'è, e chi la modifica parte da lì.
                icon=_icon_for(None, app_label, config),
            ))

        if nuove:
            # `ignore_conflicts`: due richieste insieme potrebbero provarci
            # entrambe, e il vincolo di unicità le fermerebbe.
            cls.objects.bulk_create(nuove, ignore_conflicts=True)
        return len(nuove)
