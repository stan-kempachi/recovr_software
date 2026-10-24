from django.urls import path

from . import views

app_name = "notifications"

urlpatterns = [
    path("", views.notification_list, name="notification_list"),
    path("<int:notification_id>/", views.notification_open, name="notification_open"),
    path("read-all/", views.mark_all_read, name="mark_all_read"),
]
