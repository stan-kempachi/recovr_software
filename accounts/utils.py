"""Helpers liés aux comptes et aux entreprises."""


def get_user_company(user):
    """Retourne l'entreprise principale de l'utilisateur (ou la première), sinon None."""
    if not user.is_authenticated:
        return None
    link = user.companies.filter(is_primary=True).first() or user.companies.first()
    return link.company if link else None
