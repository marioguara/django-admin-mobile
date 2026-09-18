from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from django.utils.html import format_html

from .menu import build_items
from .models import MenuIcon


@admin.register(MenuIcon)
class MenuIconAdmin(admin.ModelAdmin):
    list_display = (
        "preview",
        "app_label",
        "model_name",
        "label_override",
        "order",
        "pinned",
        "visible",
    )
    list_display_links = ("preview", "app_label")
    list_editable = ("order", "pinned", "visible")
    list_filter = ("visible", "pinned", "app_label")
    search_fields = ("app_label", "model_name", "label_override")
    change_list_template = "django_admin_mobile/menuicon_changelist.html"
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
            "Posizione nel menu",
            {
                "fields": ("order", "pinned", "visible"),
                "description": (
                    "«In evidenza» porta la voce anche nella barra di "
                    "navigazione in basso, come in una normale app."
                ),
            },
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

    # ── Pagina "Organizza il menu" ────────────────────────────────────────

    def get_urls(self):
        custom = [
            path(
                "organizza/",
                self.admin_site.admin_view(self.reorder_view),
                name="django_admin_mobile_menuicon_reorder",
            ),
        ]
        return custom + super().get_urls()

    def reorder_view(self, request):
        """Trascina le voci per cambiarne l'ordine, l'icona e la visibilità.

        L'elenco non viene dai record salvati ma dal menu vero e proprio
        (``available_apps``): così compaiono anche le voci che non hanno
        ancora una configurazione, e il record viene creato solo al salvataggio.
        """
        if not self.has_change_permission(request):
            raise PermissionDenied

        context = self.admin_site.each_context(request)

        if request.method == "POST":
            saved = self._save_order(request)
            self.message_user(
                request,
                f"Menu aggiornato: {saved} voci salvate.",
                messages.SUCCESS,
            )
            return HttpResponseRedirect(request.get_full_path())

        # Anche le voci nascoste vanno elencate: questa pagina è l'unico
        # posto da cui si possono riaccendere.
        items = build_items(
            context.get("available_apps") or [], include_hidden=True
        )
        for item in items:
            item["key"] = f"{item['app_label']}.{item['model_name']}"

        context.update(
            {
                "title": "Organizza il menu",
                "items": items,
                "opts": self.model._meta,
                "changelist_url": reverse(
                    "admin:django_admin_mobile_menuicon_changelist"
                ),
                "has_pinned": any(i["pinned"] for i in items),
            }
        )
        return render(request, "django_admin_mobile/reorder.html", context)

    def _save_order(self, request):
        keys = request.POST.getlist("entry")
        pinned = set(request.POST.getlist("pinned"))
        visible = set(request.POST.getlist("visible"))
        saved = 0
        for index, key in enumerate(keys):
            app_label, _, model_name = key.partition(".")
            if not app_label:
                continue
            icon = (request.POST.get(f"icon:{key}") or "").strip()
            obj, _created = MenuIcon.objects.get_or_create(
                app_label=app_label, model_name=model_name
            )
            obj.order = index
            obj.pinned = key in pinned
            obj.visible = key in visible
            if icon:
                obj.icon = icon
            obj.save()
            saved += 1
        return saved
