# dashboard/models.py
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Dashboard(models.Model):
    """Modèle pour stocker les tableaux de bord personnalisés des utilisateurs"""
    name = models.CharField(_("Nom"), max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dashboards")
    is_default = models.BooleanField(_("Tableau de bord par défaut"), default=False)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

    class Meta:
        verbose_name = _("Tableau de bord")
        verbose_name_plural = _("Tableaux de bord")
        unique_together = [['name', 'user']]

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class Widget(models.Model):
    """Modèle pour les widgets affichés sur les tableaux de bord"""
    TYPE_CHOICES = (
        ('line_chart', _('Graphique linéaire')),
        ('bar_chart', _('Graphique à barres')),
        ('pie_chart', _('Graphique circulaire')),
        ('kpi', _('Indicateur clé de performance')),
        ('table', _('Tableau')),
        ('alert', _('Alerte')),
    )

    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name="widgets")
    title = models.CharField(_("Titre"), max_length=100)
    widget_type = models.CharField(_("Type de widget"), max_length=20, choices=TYPE_CHOICES)
    data_source = models.CharField(_("Source de données"), max_length=100)
    filter_criteria = models.JSONField(_("Critères de filtrage"), default=dict, blank=True)
    position_x = models.IntegerField(_("Position X"))
    position_y = models.IntegerField(_("Position Y"))
    width = models.IntegerField(_("Largeur"), default=1)
    height = models.IntegerField(_("Hauteur"), default=1)
    refresh_rate = models.IntegerField(_("Taux de rafraîchissement (min)"), default=60)

    class Meta:
        verbose_name = _("Widget")
        verbose_name_plural = _("Widgets")
        ordering = ['position_y', 'position_x']

    def __str__(self):
        return f"{self.title} ({self.get_widget_type_display()})"


class SavedFilter(models.Model):
    """Modèle pour sauvegarder des filtres personnalisés"""
    name = models.CharField(_("Nom"), max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_filters")
    filter_data = models.JSONField(_("Données de filtre"))

    class Meta:
        verbose_name = _("Filtre sauvegardé")
        verbose_name_plural = _("Filtres sauvegardés")
        unique_together = [['name', 'user']]

    def __str__(self):
        return self.name


class KPI(models.Model):
    """Modèle pour définir des indicateurs clés de performance"""
    name = models.CharField(_("Nom"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    calculation_method = models.CharField(_("Méthode de calcul"), max_length=255)
    display_format = models.CharField(_("Format d'affichage"), max_length=50, default="number")
    target_value = models.FloatField(_("Valeur cible"), null=True, blank=True)
    warning_threshold = models.FloatField(_("Seuil d'avertissement"), null=True, blank=True)
    critical_threshold = models.FloatField(_("Seuil critique"), null=True, blank=True)

    class Meta:
        verbose_name = _("KPI")
        verbose_name_plural = _("KPIs")

    def __str__(self):
        return self.name