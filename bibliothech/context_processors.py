"""
Context processors pour rendre certaines données disponibles dans tous les templates
"""
from .models import Notification


def notifications_non_lues(request):
    """Ajoute le nombre de notifications non lues au contexte"""
    if request.user.is_authenticated and hasattr(request.user, 'etudiant'):
        count = request.user.etudiant.notifications.filter(lu=False).count()
        return {'notifications_non_lues_count': count}
    return {'notifications_non_lues_count': 0}
