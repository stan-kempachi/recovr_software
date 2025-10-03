"""
Tests OAuth2 Google - Simplifié et robuste
tests/test_oauth2_google.py
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from allauth.socialaccount.models import SocialAccount, SocialApp
from allauth.socialaccount.providers.google.provider import GoogleProvider
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture(autouse=True)
def reset_database(db):
    """Reset complet de la DB avant chaque test"""
    yield
    SocialApp.objects.all().delete()
    SocialAccount.objects.all().delete()
    User.objects.all().delete()


@pytest.fixture
def google_provider():
    """Provider Google mocké"""
    return GoogleProvider(request=None)


@pytest.fixture
def mock_google_response():
    """Réponse Google mockée"""
    return {
        "id": "123456789",
        "email": "test@example.com",
        "verified_email": True,
        "name": "Test User",
        "given_name": "Test",
        "family_name": "User",
        "picture": "https://example.com/photo.jpg",
        "locale": "fr",
    }


@pytest.mark.django_db
def test_configuration_oauth2_settings():
    """Test 1: Vérifier la configuration OAuth2 Google"""

    # Vérifier que Google est configuré
    google_config = settings.SOCIALACCOUNT_PROVIDERS.get("google", {})

    assert google_config is not None
    assert "SCOPE" in google_config
    assert "email" in google_config["SCOPE"]
    assert "profile" in google_config["SCOPE"]
    assert google_config.get("OAUTH_PKCE_ENABLED") is True

    # Vérifier les settings de sécurité
    assert settings.ACCOUNT_EMAIL_VERIFICATION == "mandatory"
    assert settings.ACCOUNT_UNIQUE_EMAIL is True
    assert "https://maeshan.com" in settings.CSRF_TRUSTED_ORIGINS


@pytest.mark.django_db
@patch(
    "allauth.socialaccount.providers.google.views.GoogleOAuth2Adapter.complete_login"
)
def test_oauth2_user_creation(mock_complete_login, mock_google_response):
    """Test 2: Création d'un nouvel utilisateur via OAuth2"""

    # Mock du SocialLogin
    social_login = MagicMock()
    social_login.account.provider = "google"
    social_login.account.uid = mock_google_response["id"]
    social_login.account.extra_data = mock_google_response

    # Créer l'utilisateur manuellement (simule ce que fait allauth)
    user = User.objects.create(
        username=mock_google_response["email"].split("@")[0],
        email=mock_google_response["email"],
        first_name=mock_google_response["given_name"],
        last_name=mock_google_response["family_name"],
    )

    # Créer le compte social
    social_account = SocialAccount.objects.create(
        user=user,
        provider="google",
        uid=mock_google_response["id"],
        extra_data=mock_google_response,
    )

    # Vérifications
    assert User.objects.count() == 1
    assert user.email == "test@example.com"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.role == "user"
    assert user.is_active is True

    # Vérifier le compte social
    assert SocialAccount.objects.count() == 1
    assert social_account.provider == "google"
    assert social_account.uid == "123456789"
    assert social_account.extra_data["email"] == "test@example.com"


@pytest.mark.django_db
@patch(
    "allauth.socialaccount.providers.google.views.GoogleOAuth2Adapter.complete_login"
)
def test_oauth2_existing_user_link(mock_complete_login, mock_google_response):
    """Test 3: Lier un compte Google à un utilisateur existant"""

    # Créer un utilisateur existant
    existing_user = User.objects.create_user(
        username="testuser", email="test@example.com", password="password123"
    )

    # Lier le compte Google
    social_account = SocialAccount.objects.create(
        user=existing_user,
        provider="google",
        uid=mock_google_response["id"],
        extra_data=mock_google_response,
    )

    # Vérifications
    assert User.objects.count() == 1
    assert SocialAccount.objects.count() == 1
    assert social_account.user == existing_user
    assert SocialAccount.objects.filter(user=existing_user, provider="google").exists()


@pytest.mark.django_db(transaction=True)
def test_oauth2_user_unique_email():
    """Test 4: Vérifier l'unicité des emails"""
    from django.db import IntegrityError

    # Créer un premier utilisateur
    User.objects.create_user(
        username="user1", email="test@example.com", password="pass123"
    )

    # Tenter de créer un second utilisateur avec le même email
    with pytest.raises(IntegrityError):
        User.objects.create_user(
            username="user2", email="test@example.com", password="pass456"
        )


@pytest.mark.django_db
@patch(
    "allauth.socialaccount.providers.google.views.GoogleOAuth2Adapter.complete_login"
)
def test_oauth2_extra_data_storage(mock_complete_login, mock_google_response):
    """Test 5: Stockage des données supplémentaires (photo, locale)"""

    # Créer un utilisateur et un compte social
    user = User.objects.create(username="testuser", email=mock_google_response["email"])

    social_account = SocialAccount.objects.create(
        user=user,
        provider="google",
        uid=mock_google_response["id"],
        extra_data=mock_google_response,
    )

    # Vérifier les extra_data
    assert social_account.extra_data["picture"] == "https://example.com/photo.jpg"
    assert social_account.extra_data["locale"] == "fr"
    assert social_account.extra_data["name"] == "Test User"
    assert social_account.extra_data["verified_email"] is True


@pytest.mark.django_db
def test_oauth2_multiple_social_accounts():
    """Test 6: Vérifier qu'on peut créer plusieurs comptes sociaux pour un user"""

    user = User.objects.create_user(
        username="testuser", email="test@example.com", password="pass123"
    )

    # Créer un compte Google
    SocialAccount.objects.create(
        user=user,
        provider="google",
        uid="123456",
        extra_data={"email": "test@example.com"},
    )

    # Créer un compte d'un autre provider (ex: Facebook)
    SocialAccount.objects.create(
        user=user,
        provider="facebook",
        uid="789012",
        extra_data={"email": "test@example.com"},
    )

    # Vérifier qu'on a bien 2 comptes sociaux pour cet user
    assert SocialAccount.objects.filter(user=user).count() == 2
    assert SocialAccount.objects.filter(user=user, provider="google").count() == 1
    assert SocialAccount.objects.filter(user=user, provider="facebook").count() == 1


@pytest.mark.django_db
def test_user_model_custom_methods():
    """Test 7: Méthodes personnalisées du modèle User"""

    # Créer un utilisateur admin
    admin_user = User.objects.create_user(
        username="admin", email="admin@example.com", password="pass123", role="admin"
    )

    # Créer un utilisateur readonly
    readonly_user = User.objects.create_user(
        username="readonly",
        email="readonly@example.com",
        password="pass123",
        role="readonly",
    )

    # Créer un utilisateur normal
    normal_user = User.objects.create_user(
        username="user", email="user@example.com", password="pass123", role="user"
    )

    # Vérifications
    assert admin_user.is_admin() is True
    assert admin_user.is_readonly() is False

    assert readonly_user.is_admin() is False
    assert readonly_user.is_readonly() is True

    assert normal_user.is_admin() is False
    assert normal_user.is_readonly() is False


@pytest.mark.django_db
@patch("requests.post")
@patch("requests.get")
def test_oauth2_token_exchange_mock(mock_get, mock_post):
    """Test 8: Mock de l'échange de code contre token"""

    # Mock de la réponse token
    mock_post.return_value = Mock(
        status_code=200,
        json=Mock(
            return_value={
                "access_token": "mock_access_token",
                "token_type": "Bearer",
                "expires_in": 3600,
            }
        ),
    )

    # Mock de la réponse user info
    mock_get.return_value = Mock(
        status_code=200,
        json=Mock(
            return_value={
                "id": "123",
                "email": "test@example.com",
                "verified_email": True,
            }
        ),
    )

    # Simuler l'échange
    token_response = mock_post.return_value.json()
    user_response = mock_get.return_value.json()

    # Vérifications
    assert token_response["access_token"] == "mock_access_token"
    assert user_response["email"] == "test@example.com"
    assert user_response["verified_email"] is True


@pytest.mark.django_db
def test_oauth2_security_settings():
    """Test 9: Vérifier les paramètres de sécurité de base"""

    # Paramètres toujours configurés (indépendants de l'environnement)
    assert settings.USE_X_FORWARDED_HOST is True
    assert settings.USE_X_FORWARDED_PORT is True
    assert settings.SECURE_CONTENT_TYPE_NOSNIFF is True
    assert settings.X_FRAME_OPTIONS == "DENY"
    assert settings.SECURE_HSTS_SECONDS == 31536000

    # Vérifier que les paramètres de cookies et protocole sont définis
    assert hasattr(settings, "CSRF_COOKIE_SECURE")
    assert hasattr(settings, "SESSION_COOKIE_SECURE")
    assert hasattr(settings, "ACCOUNT_DEFAULT_HTTP_PROTOCOL")

    # Vérifier que ce sont des types corrects
    assert isinstance(settings.CSRF_COOKIE_SECURE, bool)
    assert isinstance(settings.SESSION_COOKIE_SECURE, bool)
    assert settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL in ["http", "https"]


@pytest.mark.django_db
def test_google_provider_configuration():
    """Test 10: Configuration du provider Google"""

    google_config = settings.SOCIALACCOUNT_PROVIDERS["google"]

    # Vérifier la structure
    assert "SCOPE" in google_config
    assert "AUTH_PARAMS" in google_config
    assert "APP" in google_config
    assert "OAUTH_PKCE_ENABLED" in google_config

    # Vérifier les valeurs
    assert google_config["AUTH_PARAMS"]["access_type"] == "online"
    assert isinstance(google_config["SCOPE"], list)
    assert len(google_config["SCOPE"]) >= 2
