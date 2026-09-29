from django.apps import AppConfig
from django.db.models.signals import post_migrate


def _sincronizza_icone(sender, **kwargs):
    """Riempie l'elenco delle icone con i modelli registrati nell'admin.

    Dopo un `migrate` l'elenco è completo senza che nessuno debba aggiungere
    voci a mano. Gira una volta, dopo l'ultima app migrata.
    """
    from .models import MenuIcon

    try:
        MenuIcon.sincronizza()
    except Exception:
        # Un elenco incompleto è un fastidio, un `migrate` che si rompe no.
        pass


class DjangoAdminMobileConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_admin_mobile"
    verbose_name = "Admin Mobile"

    def ready(self):
        post_migrate.connect(_sincronizza_icone, sender=self)
