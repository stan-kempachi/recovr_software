# account/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Modèle utilisateur étendu avec rôles et préférences"""

    USER_ROLES = (
        ("admin", _("Administrateur")),
        ("user", _("Utilisateur")),
        ("readonly", _("Lecture seule")),
    )
    role = models.CharField(
        _("Rôle"), max_length=10, choices=USER_ROLES, default="user"
    )
    company = models.CharField(_("Entreprise"), max_length=100, blank=True)
    phone = models.CharField(_("Téléphone"), max_length=20, blank=True)
    notification_email = models.BooleanField(_("Notifications par email"), default=True)
    notification_app = models.BooleanField(
        _("Notifications dans l'application"), default=True
    )
    email = models.EmailField(_("Adresse email"), unique=True, max_length=100)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = _("Utilisateur")
        verbose_name_plural = _("Utilisateurs")

    def is_admin(self):
        return self.role == "admin"

    def is_readonly(self):
        return self.role == "readonly"


class Company(models.Model):
    """Modèle pour les entreprises (pour préparation de la phase multi-clients)"""

    name = models.CharField(_("Nom"), max_length=100)
    identifier = models.CharField(_("SIRET/SIREN"), max_length=20, unique=True)
    address = models.TextField(_("Adresse"))
    postal_code = models.CharField(_("Code postal"), max_length=10)
    city = models.CharField(_("Ville"), max_length=100)
    country = models.CharField(_("Pays"), max_length=100, default="France")
    contact_email = models.EmailField(_("Email de contact"))
    contact_phone = models.CharField(
        _("Téléphone de contact"), max_length=20, blank=True
    )
    website = models.URLField(_("Site web"), blank=True)
    logo = models.ImageField(
        _("Logo"), upload_to="company_logos/", blank=True, null=True
    )
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)

    class Meta:
        verbose_name = _("Entreprise")
        verbose_name_plural = _("Entreprises")

    def __str__(self):
        return self.name


class UserCompany(models.Model):
    """Association entre utilisateurs et entreprises"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="companies")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="users")
    is_primary = models.BooleanField(_("Entreprise principale"), default=False)

    class Meta:
        verbose_name = _("Association Utilisateur-Entreprise")
        verbose_name_plural = _("Associations Utilisateur-Entreprise")
        unique_together = [["user", "company"]]
