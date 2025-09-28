import os

from django.conf import settings
from django.db import connection
from django.http import HttpResponse, JsonResponse


def home(request):
    """
    Page d'accueil simple de bienvenue
    """
    return HttpResponse("Bienvenue sur Recovr ! Serveur en ligne ✅")


def health_check(request):
    """Endpoint de santé simple"""
    try:
        # Test basique de la DB
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        return JsonResponse(
            {
                "status": "healthy",
                "environment": os.getenv("ENVIRONMENT", "unknown"),
                "database": "connected",
                "debug": settings.DEBUG,
            }
        )
    except Exception as e:
        return JsonResponse(
            {
                "status": "unhealthy",
                "error": str(e),
                "environment": os.getenv("ENVIRONMENT", "unknown"),
            },
            status=503,
        )
