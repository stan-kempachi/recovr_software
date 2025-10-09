# accounts/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import UserCompany

User = get_user_model()


class UserCompanyInline(admin.TabularInline):
    model = UserCompany
    extra = 1


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    search_fields = ("username", "email", "first_name", "last_name")
    list_display = ("email", "username", "role", "is_superuser", "is_staff")
    inlines = [UserCompanyInline]
