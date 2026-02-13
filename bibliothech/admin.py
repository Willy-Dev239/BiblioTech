"""
Configuration de l'interface d'administration Django
"""
from django.contrib import admin
from .models import (
    Universite, Auteur, Etagere, Compartiment, EmplacementLivre,
    Livre, Personnel, Etudiant, Abonnement, Emprunt, Reservation, Notification
)

from .models import  Faculte1, Departement, Classe, Etudiant1


# Personnalisation de l'interface admin
admin.site.site_header = "Administration Bibliothèque"
admin.site.site_title = "Bibliothèque Admin"
admin.site.index_title = "Bienvenue dans l'administration de la bibliothèque"
from bibliothech.models import ParametreBibliotheque


from .models import (
    ParametreBibliotheque, CategorieEmprunteur, JourFerie,
    MessageSysteme, RegleMetier, ConfigurationEmail, HistoriqueParametres
)


@admin.register(Universite)
class UniversiteAdmin(admin.ModelAdmin):
    list_display = ['nom', 'ville', 'pays', 'actif', 'date_partenariat']
    list_filter = ['actif', 'pays', 'ville']
    search_fields = ['nom', 'ville', 'pays']
    date_hierarchy = 'date_partenariat'


@admin.register(Auteur)
class AuteurAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prenom', 'nationalite', 'date_naissance']
    list_filter = ['nationalite']
    search_fields = ['nom', 'prenom']


@admin.register(Etagere)
class EtagereAdmin(admin.ModelAdmin):
    list_display = ['code', 'salle', 'etage', 'capacite_max', 'nombre_livres']
    list_filter = ['salle', 'etage']
    search_fields = ['code', 'salle']


@admin.register(Compartiment)
class CompartimentAdmin(admin.ModelAdmin):
    list_display = ['etagere', 'numero', 'niveau', 'categorie', 'capacite']
    list_filter = ['etagere', 'niveau']
    search_fields = ['categorie']


@admin.register(EmplacementLivre)
class EmplacementLivreAdmin(admin.ModelAdmin):
    list_display = ['code_emplacement', 'compartiment', 'position', 'disponible']
    list_filter = ['disponible', 'compartiment__etagere']
    search_fields = ['code_emplacement']


class AuteurInline(admin.TabularInline):
    model = Livre.auteurs.through
    extra = 1


@admin.register(Livre)
class LivreAdmin(admin.ModelAdmin):
    list_display = ['titre', 'isbn', 'editeur', 'annee_publication', 'langue', 'disponible', 'nombre_exemplaires']
    list_filter = ['langue', 'disponible', 'etat', 'categorie']
    search_fields = ['titre', 'isbn', 'editeur']
    filter_horizontal = ['auteurs']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Personnel)
class PersonnelAdmin(admin.ModelAdmin):
    list_display = ['matricule', 'nom', 'prenom', 'role', 'universite', 'actif']
    list_filter = ['role', 'actif', 'universite']
    search_fields = ['matricule', 'nom', 'prenom', 'email']
    date_hierarchy = 'date_embauche'


@admin.register(Etudiant)
class EtudiantAdmin(admin.ModelAdmin):
    list_display = ['numero_etudiant', 'nom', 'prenom', 'niveau', 'universite', 'actif']
    list_filter = ['niveau', 'actif', 'universite', 'faculte']
    search_fields = ['numero_etudiant', 'nom', 'prenom', 'email']
    date_hierarchy = 'created_at'


@admin.register(Abonnement)
class AbonnementAdmin(admin.ModelAdmin):
    list_display = ['etudiant', 'type_abonnement', 'date_debut', 'date_fin', 'actif', 'montant']
    list_filter = ['type_abonnement', 'actif']
    search_fields = ['etudiant__nom', 'etudiant__prenom', 'etudiant__numero_etudiant']
    date_hierarchy = 'date_debut'


@admin.register(Emprunt)
class EmpruntAdmin(admin.ModelAdmin):
    list_display = ['livre', 'etudiant', 'date_emprunt', 'date_retour_prevue', 'statut', 'penalite']
    list_filter = ['statut', 'date_emprunt']
    search_fields = ['livre__titre', 'etudiant__nom', 'etudiant__prenom']
    date_hierarchy = 'date_emprunt'
    readonly_fields = ['date_emprunt', 'created_at']


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['livre', 'etudiant', 'date_reservation', 'date_expiration', 'statut']
    list_filter = ['statut', 'date_reservation']
    search_fields = ['livre__titre', 'etudiant__nom', 'etudiant__prenom']
    date_hierarchy = 'date_reservation'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['etudiant', 'type_notification', 'lu', 'created_at']
    list_filter = ['type_notification', 'lu', 'created_at']
    search_fields = ['etudiant__nom', 'etudiant__prenom', 'message']
    date_hierarchy = 'created_at'



@admin.register(ParametreBibliotheque)
class ParametreBibliothequeAdmin(admin.ModelAdmin):
    list_display = ['nom_bibliotheque', 'email', 'telephone', 'date_modification']
    readonly_fields = ['date_creation', 'date_modification']
    
    def has_add_permission(self, request):
        # Empêcher la création de plus d'une instance
        return not ParametreBibliotheque.objects.exists()

@admin.register(CategorieEmprunteur)
class CategorieEmprunteurAdmin(admin.ModelAdmin):
    list_display = ['nom', 'duree_emprunt', 'nombre_emprunts_max', 'cotisation_annuelle', 'actif']
    list_filter = ['actif', 'priorite_reservation']
    search_fields = ['nom', 'description']

@admin.register(JourFerie)
class JourFerieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'date', 'recurrent', 'fermeture_totale']
    list_filter = ['recurrent', 'fermeture_totale']
    ordering = ['date']

@admin.register(MessageSysteme)
class MessageSystemeAdmin(admin.ModelAdmin):
    list_display = ['titre', 'type_message', 'cible', 'date_debut', 'date_fin', 'actif', 'prioritaire']
    list_filter = ['type_message', 'cible', 'actif', 'prioritaire']
    search_fields = ['titre', 'message']

@admin.register(RegleMetier)
class RegleMetierAdmin(admin.ModelAdmin):
    list_display = ['code', 'nom', 'actif', 'date_modification']
    list_filter = ['actif']
    search_fields = ['code', 'nom']
    readonly_fields = ['date_creation', 'date_modification']

@admin.register(ConfigurationEmail)
class ConfigurationEmailAdmin(admin.ModelAdmin):
    list_display = ['type_email', 'sujet', 'actif']
    list_filter = ['actif', 'type_email']

@admin.register(HistoriqueParametres)
class HistoriqueParametresAdmin(admin.ModelAdmin):
    list_display = ['parametre_modifie', 'utilisateur', 'date_modification']
    list_filter = ['date_modification']
    search_fields = ['parametre_modifie', 'utilisateur']
    readonly_fields = ['date_modification']





# @admin.register(Universite)
# class UniversiteAdmin(admin.ModelAdmin):
#     list_display = ['nom', 'code', 'adresse']
#     search_fields = ['nom', 'code']


@admin.register(Faculte1)
class FaculteAdmin(admin.ModelAdmin):
    list_display = ['nom', 'code', 'universite']
    list_filter = ['universite']
    search_fields = ['nom', 'code']


@admin.register(Departement)
class DepartementAdmin(admin.ModelAdmin):
    list_display = ['nom', 'code', 'sigle', 'get_faculte', 'get_universite']
    list_filter = ['faculte', 'faculte__universite']  # Correction ici
    search_fields = ['nom', 'code', 'sigle', 'faculte__nom']
    
    def get_faculte(self, obj):
        """Affiche la faculté"""
        return obj.faculte.nom
    get_faculte.short_description = 'Faculté'
    get_faculte.admin_order_field = 'faculte__nom'
    
    def get_universite(self, obj):
        """Affiche l'université via la faculté"""
        return obj.faculte.universite.nom
    get_universite.short_description = 'Université'
    get_universite.admin_order_field = 'faculte__universite__nom'
@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ['nom', 'niveau', 'departement', 'faculte', 'annee_academique']
    list_filter = ['niveau', 'annee_academique', 'faculte']
    search_fields = ['nom', 'niveau']


@admin.register(Etudiant1)
class Etudiant1Admin(admin.ModelAdmin):
    list_display = [
        'matricule', 'nom', 'prenom', 'email', 
        'universite', 'faculte', 'statut', 'sync_depuis_api'
    ]
    list_filter = [
        'statut', 'sync_depuis_api', 'universite', 
        'faculte', 'niveau_etude'
    ]
    search_fields = ['matricule', 'nom', 'prenom', 'email', 'api_id']
    readonly_fields = ['derniere_sync', 'date_creation', 'date_modification']
    
    fieldsets = (
        ('Identification', {
            'fields': ('matricule', 'api_id', 'email')
        }),
        ('Informations personnelles', {
            'fields': ('nom', 'prenom', 'date_naissance', 'lieu_naissance', 'sexe')
        }),
        ('Contact', {
            'fields': ('telephone', 'adresse')
        }),
        ('Hiérarchie académique', {
            'fields': ('universite', 'faculte', 'departement', 'classe')
        }),
        ('Informations académiques', {
            'fields': ('niveau_etude', 'annee_academique', 'statut')
        }),
        ('Synchronisation', {
            'fields': ('sync_depuis_api', 'derniere_sync', 'date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
        ('Données brutes', {
            'fields': ('donnees_api_brutes',),
            'classes': ('collapse',)
        })
    )
    
    actions = ['synchroniser_depuis_api']
    
    def synchroniser_depuis_api(self, request, queryset):
        """Action pour synchroniser les étudiants sélectionnés"""
        succes = 0
        erreurs = 0
        
        for etudiant in queryset:
            try:
                Etudiant1.recuperer_depuis_api(matricule=etudiant.matricule)
                succes += 1
            except Exception:
                erreurs += 1
        
        self.message_user(
            request, 
            f"{succes} étudiant(s) synchronisé(s). {erreurs} erreur(s)."
        )
    
    synchroniser_depuis_api.short_description = "Synchroniser depuis l'API"
    
    
    
