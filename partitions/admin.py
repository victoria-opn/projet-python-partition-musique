from django.contrib import admin
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ["id", "utilisateur", "tonalite", "statut", "date_creation"]
    list_filter = ["statut", "tonalite"]
    readonly_fields = ["id", "date_creation"]