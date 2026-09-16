from django.core.validators import RegexValidator
from django.db import migrations, models


HEX_COLOR_VALIDATOR = RegexValidator(
    regex=r"^#(?:[0-9a-fA-F]{3}){1,2}$",
    message="Il colore deve essere in formato esadecimale, es. #417690.",
)


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="MenuIcon",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "app_label",
                    models.CharField(
                        help_text="Etichetta dell'app Django (es. `pazienti`, `visite`, `auth`).",
                        max_length=100,
                    ),
                ),
                (
                    "model_name",
                    models.CharField(
                        blank=True,
                        help_text=(
                            "Nome del modello in minuscolo (es. `paziente`). "
                            "Lascia vuoto per assegnare l'icona all'intera app."
                        ),
                        max_length=100,
                    ),
                ),
                (
                    "icon",
                    models.CharField(
                        default="\U0001f4cb",
                        help_text="Emoji o carattere unicode da mostrare come icona del bottone.",
                        max_length=16,
                    ),
                ),
                (
                    "color",
                    models.CharField(
                        default="#417690",
                        help_text="Colore del testo / bordo (formato #RRGGBB).",
                        max_length=7,
                        validators=[HEX_COLOR_VALIDATOR],
                    ),
                ),
                (
                    "background",
                    models.CharField(
                        default="#ffffff",
                        help_text="Colore di sfondo del bottone (formato #RRGGBB).",
                        max_length=7,
                        validators=[HEX_COLOR_VALIDATOR],
                    ),
                ),
                (
                    "label_override",
                    models.CharField(
                        blank=True,
                        help_text="Se valorizzato, sovrascrive il nome mostrato sul bottone.",
                        max_length=100,
                    ),
                ),
                (
                    "order",
                    models.IntegerField(
                        default=0,
                        help_text="Ordinamento crescente all'interno della griglia mobile.",
                    ),
                ),
                (
                    "visible",
                    models.BooleanField(
                        default=True,
                        help_text="Se disattivato, il bottone non compare nel menu mobile.",
                    ),
                ),
            ],
            options={
                "verbose_name": "Icona menu mobile",
                "verbose_name_plural": "Icone menu mobile",
                "ordering": ("order", "app_label", "model_name"),
                "unique_together": {("app_label", "model_name")},
            },
        ),
    ]
