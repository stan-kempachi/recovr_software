"""
Contrôle quotidien des factures : recalcule les retards et la conformité,
puis notifie les utilisateurs de l'entreprise (une alerte par facture et par jour).
"""

from django.core.management.base import BaseCommand
from django.urls import reverse
from django.utils import timezone

from accounts.models import UserCompany
from invoices.models import Invoice
from notifications.services import already_notified_today, notify


class Command(BaseCommand):
    help = "Recalcule retards/conformité des factures et envoie les alertes."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-notify", action="store_true", help="Recalcul seul, sans alertes."
        )
        parser.add_argument(
            "--email", action="store_true", help="Envoie aussi les alertes par email."
        )

    def handle(self, *args, **options):
        today = timezone.localdate()
        invoices = Invoice.objects.exclude(status="paid").select_related(
            "client", "company"
        )
        recipients_cache = {}
        overdue = non_compliant = sent = 0

        for invoice in invoices:
            days = invoice.compute_days_overdue(today)
            compliant = invoice.update_compliance_status()
            if days > 0:
                overdue += 1
            if not compliant:
                non_compliant += 1
            if options["no_notify"]:
                continue

            link = reverse("invoices:invoice_detail", args=[invoice.id])
            company_id = invoice.company_id
            if company_id not in recipients_cache:
                recipients_cache[company_id] = [
                    uc.user
                    for uc in UserCompany.objects.filter(
                        company_id=company_id, user__is_active=True
                    ).select_related("user")
                    if uc.user.role in ("admin", "user")
                ]
            for user in recipients_cache[company_id]:
                if days > 0 and not already_notified_today(
                    user, "invoice_overdue", link
                ):
                    notify(
                        user,
                        "invoice_overdue",
                        f"Facture {invoice.invoice_number} en retard de {days} j",
                        f"{invoice.client.name} — {invoice.amount_ttc} TTC, "
                        f"échéance {invoice.due_date:%d/%m/%Y}.",
                        link=link,
                        priority="urgent" if days >= 30 else "high",
                        send_email=options["email"],
                    )
                    sent += 1
                if (
                    not compliant
                    and invoice.status in Invoice.OPEN_STATUSES
                    and not already_notified_today(user, "invoice_non_compliant", link)
                ):
                    notify(
                        user,
                        "invoice_non_compliant",
                        f"Facture {invoice.invoice_number} : documents manquants",
                        "Manquant : " + ", ".join(invoice.missing_documents()),
                        link=link,
                        priority="normal",
                        send_email=options["email"],
                    )
                    sent += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"{invoices.count()} factures ouvertes — {overdue} en retard, "
                f"{non_compliant} non conformes, {sent} notification(s) créée(s)."
            )
        )
