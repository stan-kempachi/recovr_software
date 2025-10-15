import json
from datetime import date, timedelta
from unittest.mock import Mock, patch

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from accounts.models import Company, UserCompany
from core.models import Currency
from invoices.models import Client, Invoice, InvoiceDocument

User = get_user_model()


# ==================== FIXTURES ====================


@pytest.fixture
def user():
    """Utilisateur de test"""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def admin_user():
    """Utilisateur admin de test"""
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass123",
        first_name="Admin",
        last_name="User",
    )


@pytest.fixture
def company(db):
    """Entreprise de test"""
    return Company.objects.create(
        name="Test Company",
        identifier="12345678901234",
        address="10 rue de Paris",
        postal_code="75000",
        city="Paris",
        country="France",
        contact_email="company@example.com",
    )


@pytest.fixture
def other_company(db):
    """Autre entreprise pour tester les permissions"""
    return Company.objects.create(
        name="Other Company",
        identifier="98765432109876",
        address="20 avenue de Lyon",
        postal_code="69000",
        city="Lyon",
        country="France",
        contact_email="other@example.com",
    )


@pytest.fixture
def company_user_link(user, company):
    """Lien entre utilisateur et entreprise"""
    return UserCompany.objects.create(
        user=user,
        company=company,
        is_primary=True,
    )


@pytest.fixture
def currency(db):
    """Devise de test"""
    return Currency.objects.create(
        code="EUR",
        name="Euro",
        symbol="€",
    )


@pytest.fixture
def client_model(company):
    """Client de test (modèle Client, pas le client de test Django)"""
    return Client.objects.create(
        company=company,
        name="Test Client",
        identifier="12345678900000",
        contact_name="John Doe",
        contact_email="client@example.com",
        contact_phone="0123456789",
        address="10 rue du Client",
        postal_code="75000",
        city="Paris",
        country="France",
    )


@pytest.fixture
def invoice(company, client_model, currency, user):
    """Facture de test"""
    return Invoice.objects.create(
        company=company,
        client=client_model,
        invoice_number="INV-2025-001",
        external_reference="EXT-001",
        platform="chorus_pro",
        platform_id="CHORUS-123",
        amount_ht=1000.00,
        amount_ttc=1200.00,
        vat_amount=200.00,
        currency=currency,
        issue_date=date.today(),
        due_date=date.today() + timedelta(days=30),
        status="draft",
        created_by=user,
    )


@pytest.fixture
def paid_invoice(company, client_model, currency, user):
    """Facture payée"""
    return Invoice.objects.create(
        company=company,
        client=client_model,
        invoice_number="INV-2025-002",
        platform="chorus_pro",
        amount_ht=2000.00,
        amount_ttc=2400.00,
        vat_amount=400.00,
        currency=currency,
        issue_date=date.today() - timedelta(days=60),
        due_date=date.today() - timedelta(days=30),
        payment_date=date.today() - timedelta(days=25),
        status="paid",
        created_by=user,
    )


@pytest.fixture
def overdue_invoice(company, client_model, currency, user):
    """Facture en retard"""
    return Invoice.objects.create(
        company=company,
        client=client_model,
        invoice_number="INV-2025-003",
        platform="chorus_pro",
        amount_ht=1500.00,
        amount_ttc=1800.00,
        vat_amount=300.00,
        currency=currency,
        issue_date=date.today() - timedelta(days=45),
        due_date=date.today() - timedelta(days=5),
        status="submitted",
        created_by=user,
        days_overdue=5,
    )


@pytest.fixture
def pdf_file():
    """Fichier PDF de test"""
    # Utiliser un PDF simple sans caractères spéciaux
    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n"
        b"2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n"
        b"3 0 obj\n<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>\nendobj\n"
        b"xref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n"
        b"0000000058 00000 n\n0000000115 00000 n\n"
        b"trailer\n<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF"
    )
    return SimpleUploadedFile(
        "test_invoice.pdf", pdf_content, content_type="application/pdf"
    )


@pytest.fixture
def invoice_document(invoice, user, pdf_file):
    """Document de facture de test"""
    return InvoiceDocument.objects.create(
        invoice=invoice,
        document_type="invoice",
        file=pdf_file,
        reference="DOC-001",
        description="Facture principale",
        uploaded_by=user,
    )


# ==================== TESTS MODELS ====================


@pytest.mark.django_db
class TestClientModel:
    def test_create_client(self, company):
        client = Client.objects.create(
            company=company,
            name="New Client",
            identifier="98765432100000",
            address="15 avenue Test",
            postal_code="69000",
            city="Lyon",
        )
        assert client.name == "New Client"
        assert str(client) == "New Client"
        assert client.company == company

    def test_client_unique_together(self, company, client_model):
        with pytest.raises(Exception):
            Client.objects.create(
                company=company,
                name="Duplicate",
                identifier=client_model.identifier,
                address="Test",
                postal_code="75000",
                city="Paris",
            )


@pytest.mark.django_db
class TestInvoiceModel:
    def test_create_invoice(self, invoice):
        assert invoice.invoice_number == "INV-2025-001"
        assert invoice.status == "draft"
        assert str(invoice) == f"INV-2025-001 - {invoice.client.name}"

    def test_invoice_unique_together(self, company, client_model, currency, user):
        Invoice.objects.create(
            company=company,
            client=client_model,
            invoice_number="INV-UNIQUE",
            platform="chorus_pro",
            amount_ht=100,
            amount_ttc=120,
            vat_amount=20,
            currency=currency,
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            created_by=user,
        )

        with pytest.raises(Exception):
            Invoice.objects.create(
                company=company,
                client=client_model,
                invoice_number="INV-UNIQUE",
                platform="chorus_pro",
                amount_ht=200,
                amount_ttc=240,
                vat_amount=40,
                currency=currency,
                issue_date=date.today(),
                due_date=date.today() + timedelta(days=30),
                created_by=user,
            )

    def test_update_compliance_status_all_docs_present(self, invoice, user):
        # Créer tous les documents requis (types en minuscules selon DOC_TYPE_CHOICES)
        InvoiceDocument.objects.create(
            invoice=invoice,
            document_type="invoice",  # minuscule
            file=SimpleUploadedFile("facture.pdf", b"content"),
            uploaded_by=user,
        )
        InvoiceDocument.objects.create(
            invoice=invoice,
            document_type="po",  # minuscule
            file=SimpleUploadedFile("po.pdf", b"content"),
            uploaded_by=user,
        )
        InvoiceDocument.objects.create(
            invoice=invoice,
            document_type="bl",  # minuscule
            file=SimpleUploadedFile("bl.pdf", b"content"),
            uploaded_by=user,
        )

        result = invoice.update_compliance_status()
        assert result is True
        assert invoice.is_compliant is True

    def test_update_compliance_status_missing_docs(self, invoice, user):
        # Créer seulement un document
        InvoiceDocument.objects.create(
            invoice=invoice,
            document_type="invoice",
            file=SimpleUploadedFile("facture.pdf", b"content"),
            uploaded_by=user,
        )

        result = invoice.update_compliance_status()
        assert result is False
        assert invoice.is_compliant is False

    def test_update_compliance_status_no_docs(self, invoice):
        result = invoice.update_compliance_status()
        assert result is False
        assert invoice.is_compliant is False


@pytest.mark.django_db
class TestInvoiceDocumentModel:
    def test_create_document(self, invoice, user, pdf_file):
        doc = InvoiceDocument.objects.create(
            invoice=invoice,
            document_type="invoice",
            file=pdf_file,
            reference="REF-001",
            description="Test document",
            uploaded_by=user,
        )
        assert doc.document_type == "invoice"
        assert doc.invoice == invoice
        assert str(doc) == f"Facture - {invoice.invoice_number}"

    def test_document_without_invoice(self, user, pdf_file):
        """Test création d'un document sans facture associée (quick upload)"""
        doc = InvoiceDocument.objects.create(
            invoice=None,
            document_type="po",
            file=pdf_file,
            reference="ORPHAN-001",
            uploaded_by=user,
        )
        assert doc.invoice is None
        assert doc.document_type == "po"


# ==================== TESTS UPLOAD_DOCUMENT VIEW ====================


@pytest.mark.django_db
class TestUploadDocument:
    def test_upload_document_get_without_invoice(self, client, user, company_user_link):
        client.force_login(user)
        url = reverse("invoices:upload_document")
        response = client.get(url)
        assert response.status_code == 200
        assert "form" in response.context

    def test_upload_document_get_with_invoice(
        self, client, user, company_user_link, invoice
    ):
        client.force_login(user)
        url = reverse("invoices:upload_document", kwargs={"invoice_id": invoice.id})
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["invoice"] == invoice

    @patch("invoices.views.validate_invoice_document")
    def test_upload_document_post_success(
        self, mock_validate, client, user, company_user_link, invoice, pdf_file
    ):
        mock_validate.return_value = {"is_valid": True, "message": "Validation réussie"}

        client.force_login(user)
        url = reverse("invoices:upload_document", kwargs={"invoice_id": invoice.id})

        response = client.post(
            url,
            {
                "invoice": invoice.id,
                "document_type": "invoice",
                "file": pdf_file,
                "reference": "TEST-001",
                "description": "Test upload",
                "source": "dashboard",  # Pour éviter l'erreur de redirection
            },
        )

        assert response.status_code == 302
        assert InvoiceDocument.objects.filter(invoice=invoice).exists()
        doc = InvoiceDocument.objects.get(invoice=invoice)
        assert doc.uploaded_by == user
        assert doc.document_type == "invoice"

    @patch("invoices.views.validate_invoice_document")
    def test_upload_document_ajax_success(
        self, mock_validate, client, user, company_user_link, invoice, pdf_file
    ):
        mock_validate.return_value = {"is_valid": True, "message": "Validation réussie"}

        client.force_login(user)
        url = reverse("invoices:upload_document", kwargs={"invoice_id": invoice.id})

        response = client.post(
            url,
            {
                "invoice": invoice.id,
                "document_type": "invoice",
                "file": pdf_file,
                "reference": "AJAX-001",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["success"] is True
        assert "message" in data

    @patch("invoices.views.validate_invoice_document")
    def test_upload_document_quick_upload(
        self, mock_validate, client, user, company_user_link, pdf_file
    ):
        mock_validate.return_value = {"is_valid": True, "message": "Validation réussie"}

        client.force_login(user)
        url = reverse("invoices:upload_document")

        response = client.post(
            url,
            {
                "document_type": "po",
                "file": pdf_file,
                "reference": "QUICK-001",
                "is_quick_upload": "true",
                "source": "dashboard",  # Pour rediriger vers dashboard
            },
        )

        assert response.status_code == 302
        doc = InvoiceDocument.objects.get(reference="QUICK-001")
        assert doc.invoice is None
        assert doc.document_type == "po"

    @patch("invoices.views.validate_invoice_document")
    def test_upload_document_with_validation_warning(
        self, mock_validate, client, user, company_user_link, invoice, pdf_file
    ):
        mock_validate.return_value = {
            "is_valid": False,
            "message": "Le document ne contient pas toutes les informations",
        }

        client.force_login(user)
        url = reverse("invoices:upload_document", kwargs={"invoice_id": invoice.id})

        response = client.post(
            url,
            {
                "invoice": invoice.id,
                "document_type": "invoice",
                "file": pdf_file,
                "source": "dashboard",
            },
        )

        assert response.status_code == 302
        # Le document doit quand même être créé malgré l'avertissement
        assert InvoiceDocument.objects.filter(invoice=invoice).exists()

    def test_upload_document_updates_compliance(
        self, client, user, company_user_link, invoice
    ):
        """Test que l'upload met à jour le statut de conformité"""
        client.force_login(user)
        url = reverse("invoices:upload_document", kwargs={"invoice_id": invoice.id})

        # Upload facture
        with patch("invoices.views.validate_invoice_document") as mock_validate:
            mock_validate.return_value = {"is_valid": True, "message": "OK"}
            client.post(
                url,
                {
                    "invoice": invoice.id,
                    "document_type": "invoice",
                    "file": SimpleUploadedFile("f.pdf", b"content"),
                },
            )

        invoice.refresh_from_db()
        assert invoice.is_compliant is False  # Pas encore tous les docs

        # Upload PO
        with patch("invoices.views.validate_invoice_document") as mock_validate:
            mock_validate.return_value = {"is_valid": True, "message": "OK"}
            client.post(
                url,
                {
                    "invoice": invoice.id,
                    "document_type": "po",
                    "file": SimpleUploadedFile("po.pdf", b"content"),
                },
            )

        # Upload BL
        with patch("invoices.views.validate_invoice_document") as mock_validate:
            mock_validate.return_value = {"is_valid": True, "message": "OK"}
            client.post(
                url,
                {
                    "invoice": invoice.id,
                    "document_type": "bl",
                    "file": SimpleUploadedFile("bl.pdf", b"content"),
                },
            )

        invoice.refresh_from_db()
        assert invoice.is_compliant is True


# ==================== TESTS DOWNLOAD_DOCUMENT ====================


@pytest.mark.django_db
class TestDownloadDocument:
    def test_download_document_success(
        self, client, user, company_user_link, invoice_document
    ):
        client.force_login(user)
        url = reverse(
            "invoices:download_document", kwargs={"document_id": invoice_document.id}
        )
        response = client.get(url)
        assert response.status_code == 200
        assert response["Content-Type"] == "application/pdf"

    def test_download_document_not_found(self, client, user, company_user_link):
        client.force_login(user)
        url = reverse("invoices:download_document", kwargs={"document_id": 99999})
        response = client.get(url)
        assert response.status_code == 404


# ==================== TESTS DELETE_DOCUMENT ====================


@pytest.mark.django_db
class TestDeleteDocument:
    @patch("os.path.isfile")
    @patch("os.remove")
    def test_delete_document_success(
        self,
        mock_remove,
        mock_isfile,
        client,
        user,
        company_user_link,
        invoice_document,
    ):
        mock_isfile.return_value = True

        client.force_login(user)
        doc_id = invoice_document.id

        url = reverse("invoices:delete_document", kwargs={"document_id": doc_id})
        response = client.post(url)

        # Devrait rediriger vers document_list car pas de vue invoice_detail
        assert response.status_code == 302
        assert not InvoiceDocument.objects.filter(id=doc_id).exists()
        mock_remove.assert_called_once()

    @patch("os.path.isfile")
    def test_delete_document_without_invoice(
        self, mock_isfile, client, user, company_user_link
    ):
        mock_isfile.return_value = False

        # Créer un document orphelin
        doc = InvoiceDocument.objects.create(
            invoice=None,
            document_type="other",
            file=SimpleUploadedFile("test.pdf", b"content"),
            uploaded_by=user,
        )

        client.force_login(user)
        url = reverse("invoices:delete_document", kwargs={"document_id": doc.id})
        response = client.post(url)

        assert response.status_code == 302
        assert not InvoiceDocument.objects.filter(id=doc.id).exists()


# ==================== TESTS API ENDPOINTS ====================


@pytest.mark.django_db
class TestApiInvoiceList:
    def test_api_invoice_list_success(self, client, user, company_user_link, invoice):
        client.force_login(user)
        url = reverse("invoices:api_invoice_list")
        response = client.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data) == 1
        assert data[0]["invoice_number"] == "INV-2025-001"
        assert data[0]["client"]["name"] == invoice.client.name

    def test_api_invoice_list_multiple_companies(
        self, client, user, company, other_company, client_model, currency
    ):
        # Lier l'utilisateur aux deux entreprises
        UserCompany.objects.create(user=user, company=company, is_primary=True)
        UserCompany.objects.create(user=user, company=other_company, is_primary=False)

        # Créer des factures dans les deux entreprises
        Invoice.objects.create(
            company=company,
            client=client_model,
            invoice_number="INV-001",
            platform="chorus_pro",
            amount_ht=100,
            amount_ttc=120,
            vat_amount=20,
            currency=currency,
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
        )

        other_client = Client.objects.create(
            company=other_company,
            name="Other Client",
            identifier="99999999900000",
            address="Test",
            postal_code="69000",
            city="Lyon",
        )

        Invoice.objects.create(
            company=other_company,
            client=other_client,
            invoice_number="INV-002",
            platform="chorus_pro",
            amount_ht=200,
            amount_ttc=240,
            vat_amount=40,
            currency=currency,
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
        )

        client.force_login(user)
        url = reverse("invoices:api_invoice_list")
        response = client.get(url)

        data = json.loads(response.content)
        assert len(data) == 2

    def test_api_invoice_list_empty(self, client, user, company_user_link):
        client.force_login(user)
        url = reverse("invoices:api_invoice_list")
        response = client.get(url)

        data = json.loads(response.content)
        assert len(data) == 0


@pytest.mark.django_db
class TestApiDocumentTypes:
    def test_api_document_types(self, client, user):
        client.force_login(user)
        url = reverse("invoices:api_document_types")
        response = client.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data) > 0
        assert any(doc["id"] == "invoice" for doc in data)
        assert any(doc["id"] == "po" for doc in data)
        assert any(doc["id"] == "bl" for doc in data)


@pytest.mark.django_db
class TestDocumentList:
    def test_document_list_success(
        self, client, user, company_user_link, invoice_document
    ):
        client.force_login(user)
        url = reverse("invoices:document_list")
        response = client.get(url)

        assert response.status_code == 200
        assert "documents" in response.context
        assert invoice_document in response.context["documents"]

    def test_document_list_pagination(self, client, user, company_user_link, invoice):
        # Créer plus de 20 documents
        for i in range(25):
            InvoiceDocument.objects.create(
                invoice=invoice,
                document_type="other",
                file=SimpleUploadedFile(f"doc{i}.pdf", b"content"),
                uploaded_by=user,
            )

        client.force_login(user)
        url = reverse("invoices:document_list")
        response = client.get(url)

        assert response.status_code == 200
        assert len(response.context["page_obj"]) == 20

    def test_document_list_filter_by_user(
        self, client, user, admin_user, company_user_link, invoice
    ):
        # Document de l'utilisateur
        user_doc = InvoiceDocument.objects.create(
            invoice=invoice,
            document_type="invoice",
            file=SimpleUploadedFile("user.pdf", b"content"),
            uploaded_by=user,
        )

        # Document d'un autre utilisateur
        other_doc = InvoiceDocument.objects.create(
            invoice=invoice,
            document_type="po",
            file=SimpleUploadedFile("admin.pdf", b"content"),
            uploaded_by=admin_user,
        )

        # Utilisateur non-staff ne voit que ses propres documents
        client.force_login(user)
        url = reverse("invoices:document_list")
        response = client.get(url)

        documents = list(response.context["documents"])
        assert user_doc in documents
        # Non-staff ne voit que ses propres docs selon la vue
        assert other_doc not in documents

    def test_document_list_staff_sees_all(
        self, client, admin_user, company_user_link, invoice, user
    ):
        # Document d'un utilisateur normal
        user_doc = InvoiceDocument.objects.create(
            invoice=invoice,
            document_type="invoice",
            file=SimpleUploadedFile("user.pdf", b"content"),
            uploaded_by=user,
        )

        client.force_login(admin_user)
        url = reverse("invoices:document_list")
        response = client.get(url)

        assert user_doc in response.context["documents"]


# ==================== TESTS VALIDATORS ====================


@pytest.mark.django_db
class TestValidators:
    def test_validate_facture_pdf_success(self, invoice, user):
        from invoices.validators import validate_invoice_document

        pdf_content = b"%PDF-1.4\nFacture No 123\nMontant Total: 1000 EUR"
        pdf_file = SimpleUploadedFile(
            "facture.pdf", pdf_content, content_type="application/pdf"
        )

        doc = InvoiceDocument.objects.create(
            invoice=invoice,
            document_type="FACTURE",
            file=pdf_file,
            uploaded_by=user,
        )

        with patch("PyPDF2.PdfReader") as mock_pdf:
            mock_page = Mock()
            mock_page.extract_text.return_value = "Facture No 123 Montant Total: 1000"
            mock_pdf.return_value.pages = [mock_page]

            result = validate_invoice_document(doc)
            assert result["is_valid"] is True

    def test_validate_document_too_large(self, invoice, user):
        from invoices.validators import validate_invoice_document

        large_file = SimpleUploadedFile("large.pdf", b"x" * (11 * 1024 * 1024))
        doc = InvoiceDocument.objects.create(
            invoice=invoice,
            document_type="FACTURE",
            file=large_file,
            uploaded_by=user,
        )

        result = validate_invoice_document(doc)
        assert result["is_valid"] is False
        assert "trop volumineux" in result["message"]

    def test_validate_facture_wrong_format(self, invoice, user):
        from invoices.validators import validate_facture_document

        doc = Mock()
        doc.document_type = "FACTURE"
        doc.file.name = "document.txt"

        result = validate_facture_document(doc, ".txt")
        assert result["is_valid"] is False
        assert "Format non supporté" in result["message"]


# ==================== TESTS INTEGRATION ====================


@pytest.mark.django_db
class TestInvoiceDocumentIntegration:
    def test_full_workflow(self, client, user, company_user_link, invoice):
        """Test du workflow complet: création, upload, validation, téléchargement, suppression"""
        client.force_login(user)

        # 1. Upload d'un document
        url = reverse("invoices:upload_document", kwargs={"invoice_id": invoice.id})
        with patch("invoices.views.validate_invoice_document") as mock_validate:
            mock_validate.return_value = {"is_valid": True, "message": "OK"}
            response = client.post(
                url,
                {
                    "invoice": invoice.id,
                    "document_type": "invoice",
                    "file": SimpleUploadedFile("test.pdf", b"content"),
                    "reference": "WORKFLOW-001",
                    "source": "dashboard",
                },
            )

        assert response.status_code == 302
        doc = InvoiceDocument.objects.get(reference="WORKFLOW-001")

        # 2. Téléchargement du document
        download_url = reverse(
            "invoices:download_document", kwargs={"document_id": doc.id}
        )
        response = client.get(download_url)
        assert response.status_code == 200

        # 3. Suppression du document
        with patch("os.path.isfile") as mock_isfile, patch("os.remove"):
            mock_isfile.return_value = True
            delete_url = reverse(
                "invoices:delete_document", kwargs={"document_id": doc.id}
            )
            response = client.post(delete_url)

        assert response.status_code == 302
        assert not InvoiceDocument.objects.filter(id=doc.id).exists()
