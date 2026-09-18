from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_admin_mobile", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="menuicon",
            name="pinned",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Se attivo, la voce compare anche nella barra di navigazione "
                    "in basso, come in una normale app per telefono."
                ),
                verbose_name="In evidenza",
            ),
        ),
    ]
