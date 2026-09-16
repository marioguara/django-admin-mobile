from django.contrib import admin
from django.utils.html import format_html

from .models import MenuIcon


@admin.register(MenuIcon)
class MenuIconAdmin(admin.ModelAdmin):
    list_display = (
        "preview",
        "app_label",
        "model_name",
        "label_override",
        "order",
        "visible",
    )
    list_display_links = ("preview", "app_label")
    list_editable = ("order", "visible")
    list_filter = ("visible", "app_label")
    search_fields = ("app_label", "model_name", "label_override")
    fieldsets = (
        (
            "Destinazione",
            {
                "fields": ("app_label", "model_name", "label_override"),
                "description": (
                    "Indica per quale voce dell'admin Django questa icona deve "
                    "essere applicata. Lascia `model_name` vuoto per fare "
                    "riferimento all'intera app."
                ),
            },
        ),
        (
            "Aspetto",
            {"fields": ("icon", "color", "background")},
        ),
        (
            "Ordinamento e visibilità",
            {"fields": ("order", "visible")},
        ),
    )

    @admin.display(description="Anteprima")
    def preview(self, obj):
        return format_html(
            '<span style="display:inline-flex;align-items:center;justify-content:center;'
            "width:44px;height:44px;border-radius:12px;font-size:22px;"
            'border:2px solid {color};background:{bg};color:{color};">{icon}</span>',
            color=obj.color,
            bg=obj.background,
            icon=obj.icon,
        )
