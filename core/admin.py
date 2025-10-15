# Register your models here.
from django.contrib import admin

from .models import AuditLog, Country, Currency, SystemSetting


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "symbol")
    search_fields = ("code", "name")
    ordering = ("code",)


# Enregistrez également vos autres modèles core si nécessaire
@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ("key", "value")
    search_fields = ("key",)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "user", "timestamp")
    list_filter = ("action", "timestamp")
    search_fields = ("user__username", "details")
    readonly_fields = ("timestamp",)
