from django.contrib import admin

from accounts.models import Company
from tasks.models import Client

from .models import (
    Task,
    TaskAttachment,
    TaskCategory,
    TaskComment,
    TaskStatusHistory,
    TaskTemplate,
)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    search_fields = ("name", "email")


class TaskCommentInline(admin.TabularInline):
    model = TaskComment
    extra = 1  # nombre de champs vides pour créer un nouveau commentaire
    fields = ("user", "comment", "is_internal", "created_at")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("user",)


class TaskAttachmentInline(admin.TabularInline):
    model = TaskAttachment
    extra = 1
    fields = (
        "file",
        "filename",
        "file_size",
        "mime_type",
        "uploaded_by",
        "description",
        "uploaded_at",
    )
    readonly_fields = ("uploaded_at", "file_size", "mime_type")
    autocomplete_fields = ("uploaded_by",)


class TaskStatusHistoryInline(admin.TabularInline):
    model = TaskStatusHistory
    extra = 0
    fields = ("previous_status", "new_status", "changed_by", "changed_at", "notes")
    readonly_fields = ("changed_at",)
    autocomplete_fields = ("changed_by",)


# ----- Admin des modèles principaux -----


@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code")


@admin.register(TaskTemplate)
class TaskTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "task_type", "category", "default_priority", "is_active")
    list_filter = ("task_type", "category", "is_active")
    search_fields = ("name", "default_title")
    autocomplete_fields = ("category",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "company",
        "assigned_to",
        "status",
        "priority",
        "due_date",
        "is_overdue",
    )
    list_filter = (
        "status",
        "priority",
        "company",
        "assigned_to",
        "category",
        "task_type",
    )
    search_fields = (
        "title",
        "description",
        "assigned_to__username",
        "created_by__username",
        "company__name",
    )
    ordering = ("-urgency_score", "priority", "due_date")
    autocomplete_fields = (
        "assigned_to",
        "created_by",
        "company",
        "category",
        "invoice",
        "client",
    )

    inlines = [TaskCommentInline, TaskAttachmentInline, TaskStatusHistoryInline]


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ("task", "user", "is_internal", "created_at")
    list_filter = ("is_internal", "created_at")
    search_fields = ("task__title", "user__username", "comment")
    autocomplete_fields = ("user", "task")


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ("filename", "task", "uploaded_by", "uploaded_at")
    search_fields = ("filename", "task__title", "uploaded_by__username")
    autocomplete_fields = ("task", "uploaded_by")


@admin.register(TaskStatusHistory)
class TaskStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("task", "previous_status", "new_status", "changed_by", "changed_at")
    search_fields = ("task__title", "changed_by__username")
    autocomplete_fields = ("changed_by",)
