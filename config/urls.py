from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from core import views

app_name = "config"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("health/", views.health_check, name="health"),
    path("", include("core.urls", namespace="core")),
    path("accounts/", include("allauth.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("tasks/", include("tasks.urls", namespace="tasks")),
    path("invoices/", include("invoices.urls", namespace="invoices")),
]

# Servir les fichiers statiques en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
