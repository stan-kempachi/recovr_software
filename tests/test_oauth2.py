import pytest
from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.contrib.sites.models import Site


@pytest.fixture
def django_site():
    """Fixture pour obtenir le site avec ID=1"""
    try:
        site = Site.objects.get(id=1)
        return site
    except Site.DoesNotExist:
        pytest.fail("Le site avec ID=1 n'existe pas dans la table django_site")


@pytest.fixture
def google_app():
    """Fixture pour obtenir l'application sociale Google"""
    try:
        app = SocialApp.objects.get(provider="google")
        return app
    except SocialApp.DoesNotExist:
        pytest.fail("L'application OAuth Google n'est pas configurée")


def test_site_domain(django_site):
    """Test que le domaine du site correspond au domaine attendu"""
    expected_domains = ["www.maeshan.com", "maeshan.com"]
    assert any(
        domain in django_site.domain for domain in expected_domains
    ), f"Le domaine du site '{django_site.domain}' ne correspond pas aux domaines attendus {expected_domains}"


def test_google_oauth2_redirect_urls():
    """Test que les URLs de redirection OAuth2 sont correctement configurées"""
    expected_callbacks = [
        "https://www.maeshan.com/staging/accounts/google/login/callback",
        "https://www.maeshan.com/accounts/google/login/callback",
    ]

    # Vérifier si ces URLs sont configurées dans les paramètres
    oauth_config = getattr(settings, "SOCIALACCOUNT_PROVIDERS", {}).get("google", {})
    redirect_uris = oauth_config.get("OAUTH_CALLBACK_URLS", [])

    for callback in expected_callbacks:
        assert (
            callback in redirect_uris
        ), f"L'URL de callback '{callback}' n'est pas configurée"


def test_google_app_sites(google_app, django_site):
    """Test que l'application Google est associée au site correct"""
    assert (
        django_site in google_app.sites.all()
    ), f"L'application Google n'est pas associée au site {django_site.domain} (ID={django_site.id})"
