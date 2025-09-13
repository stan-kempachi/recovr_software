import os

from django.conf import settings
from django.db import connection
from django.http import JsonResponse


def health_check(request):
    """
    Endpoint de santé pour vérifier l'état de l'application
    """
    try:
        # Test de connexion à la base de données
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # Vérification des variables d'environnement critiques
    required_vars = ["SECRET_KEY", "DB_NAME", "DB_USER", "DB_HOST"]
    env_status = "healthy"
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var) and not hasattr(
            settings, var.replace("DB_", "DATABASES")
        ):
            missing_vars.append(var)

    if missing_vars:
        env_status = f"missing vars: {', '.join(missing_vars)}"

    # Statut global
    is_healthy = db_status == "healthy" and env_status == "healthy"

    response_data = {
        "status": "healthy" if is_healthy else "unhealthy",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "database": db_status,
        "environment_vars": env_status,
        "debug": settings.DEBUG,
    }

    status_code = 200 if is_healthy else 503

    return JsonResponse(response_data, status=status_code)
