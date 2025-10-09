from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tasks"
    verbose_name = "Gestion des Tâches"

    def ready(self):
        """Import des signals lors du démarrage de l'application"""
