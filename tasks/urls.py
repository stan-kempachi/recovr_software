from django.urls import path

from tasks import views

app_name = "tasks"

urlpatterns = [
    # Dashboard
    path("create/", views.create_task, name="create_task"),
    path("tasks/<int:task_id>/edit/", views.task_edit, name="task_edit"),
    # Liste et détails
    path("list/", views.task_list, name="task_list"),
    path("<int:task_id>/", views.task_detail, name="task_detail"),
    # Actions AJAX
    path("api/tasks/", views.get_tasks, name="get_tasks"),
    path(
        "<int:task_id>/update-status/", views.task_update_status, name="update_status"
    ),
    path("<int:task_id>/add-comment/", views.task_add_comment, name="add_comment"),
    path("<int:task_id>/assign/", views.task_assign, name="assign"),
    # API
    path("api/summary/", views.api_tasks_summary, name="api_summary"),
]
