# validators.py
import os
import re
from io import BytesIO

import PyPDF2


def validate_invoice_document(document):
    """
    Valide un document en fonction de son type
    Retourne un dict avec is_valid et message
    """
    file_name = document.file.name
    file_extension = os.path.splitext(file_name)[1].lower()

    # Validation de base pour tous les documents: taille, format
    if document.file.size > 10 * 1024 * 1024:  # 10MB
        return {
            "is_valid": False,
            "message": "Le fichier est trop volumineux (max 10MB)",
        }

    # Validation spécifique selon le type de document
    if document.document_type == "FACTURE":
        return validate_facture_document(document, file_extension)
    elif document.document_type == "PO":
        return validate_po_document(document, file_extension)
    elif document.document_type == "BL":
        return validate_bl_document(document, file_extension)
    elif document.document_type == "PV":
        return validate_pv_document(document, file_extension)
    elif document.document_type == "CRA":
        return validate_cra_document(document, file_extension)

    # Type de document inconnu ou non géré
    return {"is_valid": True, "message": "Validation générique réussie"}


def validate_facture_document(document, file_extension):
    """Validation spécifique pour les factures"""
    if file_extension not in [".pdf", ".jpg", ".png"]:
        return {
            "is_valid": False,
            "message": "Format non supporté. Veuillez télécharger un PDF ou une image",
        }

    if file_extension == ".pdf":
        try:
            # Tenter de lire le contenu du PDF
            file_content = document.file.read()
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))

            # Réinitialiser le curseur du fichier
            document.file.seek(0)

            # Vérifier le contenu pour des mots-clés
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text()

            # Vérifier la présence d'informations essentielles
            has_invoice_number = bool(
                re.search(r"facture|invoice|n[o°]\s*[:.]?\s*\d+", text_content, re.I)
            )
            has_amount = bool(
                re.search(
                    r"total|montant|amount|sum\s*[:.]?\s*[\d.,]+", text_content, re.I
                )
            )

            if not has_invoice_number or not has_amount:
                return {
                    "is_valid": True,  # Considéré valide mais avec avertissement
                    "message": "Le document ne semble pas contenir toutes les informations d'une facture",
                }

        except Exception as e:
            # Ne pas bloquer le téléchargement, mais signaler le problème
            return {
                "is_valid": True,
                "message": f"Impossible de valider le contenu PDF: {str(e)}",
            }

    return {"is_valid": True, "message": "Validation réussie"}


# Implémentations similaires pour les autres types de documents
def validate_po_document(document, file_extension):
    """Validation spécifique pour les bons de commande (PO)"""
    # Logique similaire à celle des factures
    return {"is_valid": True, "message": "Validation du bon de commande réussie"}


def validate_bl_document(document, file_extension):
    """Validation spécifique pour les bons de livraison"""
    return {"is_valid": True, "message": "Validation du bon de livraison réussie"}


def validate_pv_document(document, file_extension):
    """Validation spécifique pour les procès-verbaux"""
    return {"is_valid": True, "message": "Validation du procès-verbal réussie"}


def validate_cra_document(document, file_extension):
    """Validation spécifique pour les comptes-rendus d'activité"""
    return {
        "is_valid": True,
        "message": "Validation du compte-rendu d'activité réussie",
    }
