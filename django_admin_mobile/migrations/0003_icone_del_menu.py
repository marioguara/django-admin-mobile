"""Le icone valgono anche sul menu di sinistra su schermo grande."""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_admin_mobile', '0002_menuicon_pinned'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='menuicon',
            options={'ordering': ('order', 'app_label', 'model_name'), 'verbose_name': 'Icona del menu', 'verbose_name_plural': 'Icone del menu'},
        ),
        migrations.AlterField(
            model_name='menuicon',
            name='order',
            field=models.IntegerField(default=0, help_text="Ordinamento crescente all'interno del menu."),
        ),
        migrations.AlterField(
            model_name='menuicon',
            name='visible',
            field=models.BooleanField(default=True, help_text='Se disattivato, la voce non compare nel menu.'),
        ),
    ]
