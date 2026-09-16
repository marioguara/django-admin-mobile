from django.core.validators import RegexValidator
from django.db import models


HEX_COLOR_VALIDATOR = RegexValidator(
    regex=r"^#(?:[0-9a-fA-F]{3}){1,2}$",
    message="Il colore deve essere in formato esadecimale, es. #417690.",
)


class MenuIcon(models.Model):
    """Configurazione dell'icona di un'app o di un modello nel menu mobile."""

    app_label = models.CharField(
        max_length=100,
        help_text="Etichetta dell'app Django (es. `pazienti`, `visite`, `auth`).",
    )
    model_name = models.CharField(
        max_length=100,
        blank=True,
        help_text=(
            "Nome del modello in minuscolo (es. `paziente`). "
            "Lascia vuoto per assegnare l'icona all'intera app."
        ),
    )
    icon = models.CharField(
        max_length=16,
        default="📋",
        help_text="Emoji o carattere unicode da mostrare come icona del bottone.",
    )
    color = models.CharField(
        max_length=7,
        default="#417690",
        validators=[HEX_COLOR_VALIDATOR],
        help_text="Colore del testo / bordo (formato #RRGGBB).",
    )
    background = models.CharField(
        max_length=7,
        default="#ffffff",
        validators=[HEX_COLOR_VALIDATOR],
        help_text="Colore di sfondo del bottone (formato #RRGGBB).",
    )
    label_override = models.CharField(
        max_length=100,
        blank=True,
        help_text="Se valorizzato, sovrascrive il nome mostrato sul bottone.",
    )
    order = models.IntegerField(
        default=0,
        help_text="Ordinamento crescente all'interno della griglia mobile.",
    )
    visible = models.BooleanField(
        default=True,
        help_text="Se disattivato, il bottone non compare nel menu mobile.",
    )

    class Meta:
        verbose_name = "Icona menu mobile"
        verbose_name_plural = "Icone menu mobile"
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
