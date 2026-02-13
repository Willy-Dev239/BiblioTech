from django.urls import path
from . import views
from .views import users_list, user_update,register_view
from .views import (
    RechercheEtudiantView,
    creer_emprunt_etudiant,
    recherche_rapide_etudiant_api,
    SyncEtudiantsAPIView
)

# from .views import Etudiant1DetailView

urlpatterns = [
    # Authentification
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_password_view, name='change_password'),
    
    #Accueil
    path('home/', views.dashboard_home, name='home'),
    
    
    # Livres
    path('livres/', views.livre_list_view, name='livre_list'),
    path('livres/<int:pk>/', views.livre_detail_view, name='livre_detail'),
    path('livres/ajouter/', views.livre_create_view, name='livre_create'),
    path('livres/<int:pk>/modifier/', views.livre_update_view, name='livre_update'),
    path('livres/<int:pk>/supprimer/', views.livre_delete_view, name='livre_delete'),
    
    # Abonne.es
    path('abonnes/', views.etudiant_list_view, name='abonnes'),
    path('abonnes/<int:pk>/', views.etudiant_detail_view, name='etudiant_detail'),
    path('abonnes/ajouter/', views.etudiant_create_view, name='etudiant_create'),
    path('abonnes/<int:pk>/modifier/', views.etudiant_update_view, name='etudiant_update'),
    
    # Emprunts
    path('emprunts/', views.emprunt_list_view, name='emprunt_list'),
    path('emprunts/creer/', views.emprunt_create_view, name='emprunt_create'),
    path('emprunts/<int:pk>/retour/', views.emprunt_retour_view, name='emprunt_retour'),
    
    # Réservations
    path('reservations/<int:livre_pk>/creer/', views.reservation_create_view, name='reservation_create'),
    path('reservations/<int:pk>/annuler/', views.reservation_annuler_view, name='reservation_annuler'),
    
    # Abonnements
    path('abonnements/<int:etudiant_pk>/creer/', views.abonnement_create_view, name='abonnement_create'),
    
    # Notifications
    path('notifications/', views.notification_list_view, name='notification_list'),
    
    #etageres
    
    path('etageres/', views.etagere_list_view, name='etagere_list'),
    path('etageres/<int:pk>/', views.etagere_detail_view, name='etagere_detail'),
    path('etageres/create/', views.etagere_create_view, name='etagere_create'),
    path('etageres/<int:pk>/update/', views.etagere_update_view, name='etagere_update'),
    path('etageres/<int:pk>/delete/', views.etagere_delete_view, name='etagere_delete'),
     # ========== COMPARTIMENTS ==========
    path('compartiments/', views.compartiment_list_view, name='compartiment_list'),
    path('compartiments/<int:pk>/', views.compartiment_detail_view, name='compartiment_detail'),
    path('compartiments/create/', views.compartiment_create_view, name='compartiment_create'),
    path('compartiments/<int:pk>/update/', views.compartiment_update_view, name='compartiment_update'),
    path('compartiments/<int:pk>/delete/', views.compartiment_delete_view, name='compartiment_delete'),
    
    # ========== EMPLACEMENTS ==========
    path('emplacements/', views.emplacement_list_view, name='emplacement_list'),
    path('emplacements/<int:pk>/', views.emplacement_detail_view, name='emplacement_detail'),
    path('emplacements/create/', views.emplacement_create_view, name='emplacement_create'),
    path('emplacements/<int:pk>/update/', views.emplacement_update_view, name='emplacement_update'),
    path('emplacements/<int:pk>/delete/', views.emplacement_delete_view, name='emplacement_delete'),
    
    # ========== PARAMÉTRAGE ==========
    path('parametrage/', views.parametrage_dashboard_view, name='parametrage_dashboard'),
    path('parametrage/general/', views.parametres_generaux_view, name='parametres_generaux'),
    
    # Catégories d'emprunteurs
    path('parametrage/categories/', views.categorie_emprunteur_list_view, name='categorie_emprunteur_list'),
    path('parametrage/categories/create/', views.categorie_emprunteur_create_view, name='categorie_emprunteur_create'),
    path('parametrage/categories/<int:pk>/update/', views.categorie_emprunteur_update_view, name='categorie_emprunteur_update'),
    path('parametrage/categories/<int:pk>/delete/', views.categorie_emprunteur_delete_view, name='categorie_emprunteur_delete'),
    
    # Jours fériés
    path('parametrage/jours-feries/', views.jour_ferie_list_view, name='jour_ferie_list'),
    path('parametrage/jours-feries/create/', views.jour_ferie_create_view, name='jour_ferie_create'),
    path('parametrage/jours-feries/<int:pk>/update/', views.jour_ferie_update_view, name='jour_ferie_update'),
    path('parametrage/jours-feries/<int:pk>/delete/', views.jour_ferie_delete_view, name='jour_ferie_delete'),
    
    # Messages système
    path('parametrage/messages/', views.message_systeme_list_view, name='message_systeme_list'),
    path('parametrage/messages/create/', views.message_systeme_create_view, name='message_systeme_create'),
    path('parametrage/messages/<int:pk>/update/', views.message_systeme_update_view, name='message_systeme_update'),
    path('parametrage/messages/<int:pk>/delete/', views.message_systeme_delete_view, name='message_systeme_delete'),
    
    # Configuration emails
    path('parametrage/emails/', views.configuration_email_list_view, name='configuration_email_list'),
    path('parametrage/emails/<int:pk>/update/', views.configuration_email_update_view, name='configuration_email_update'),

# URLs pour les abonnements
    path('abonnements/', views.abonnement_list, name='abonnement_list'),
    path('abonnements/creer/', views.abonnement_create, name='abonnement_create'),
    path('abonnements/<int:pk>/', views.abonnement_detail, name='abonnement_detail'),
    path('abonnements/<int:pk>/modifier/', views.abonnement_update, name='abonnement_update'),
    path('abonnements/<int:pk>/supprimer/', views.abonnement_delete, name='abonnement_delete'),
    
    # URLs pour les universités
    path('universites/', views.universite_list, name='universite_list'),
    path('universites/creer/', views.universite_create, name='universite_create'),
    path('universites/<int:pk>/', views.universite_detail, name='universite_detail'),
    path('universites/<int:pk>/modifier/', views.universite_update, name='universite_update'),
    path('universites/<int:pk>/supprimer/', views.universite_delete, name='universite_delete'),
    
    # URLs pour les auteurs
    path('auteurs/', views.auteur_list, name='auteur_list'),
    path('auteurs/creer/', views.auteur_create, name='auteur_create'),
    path('auteurs/<int:pk>/', views.auteur_detail, name='auteur_detail'),
    path('auteurs/<int:pk>/modifier/', views.auteur_update, name='auteur_update'),
    path('auteurs/<int:pk>/supprimer/', views.auteur_delete, name='auteur_delete'),
    
    
     # ========== GESTION DES UTILISATEURS ==========
    
    # Récupérer tous les utilisateurs
    # GET /api/users/
    path('get_users', views.get_users, name='get_users'),
    
    # Récupérer un utilisateur par ID
    # GET /api/users/<id>/
    path('api/users/<int:user_id>/', views.get_user_by_id, name='get_user_by_id'),
    
    # Mettre à jour les droits d'un utilisateur (is_staff, is_superuser, is_active)
    # PUT/PATCH /api/users/<id>/permissions/
    path('api/users/<int:user_id>/permissions/', views.update_user_permissions, name='update_user_permissions'),
    
    # Mettre à jour toutes les infos d'un utilisateur
    # PUT /api/users/<id>/complete/
    path('api/users/<int:user_id>/complete/', views.update_user_complete, name='update_user_complete'),
    
    # Supprimer un utilisateur
    # DELETE /api/users/<id>/delete/
    path('api/users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    
    # Rechercher des utilisateurs
    # GET /api/users/search/?q=<terme>
    path('api/users/search/', views.search_users, name='search_users'),
    
    # Statistiques des utilisateurs
    # GET /api/users/stats/ttt
    path('api/users/stats/', views.get_users_stats, name='get_users_stats'),
    
    path("api/users/", users_list, name="users_list"),
    path("api/users/<int:user_id>/", user_update, name="user_update"),
    
    # path('register/', register_view, name='register'),
    
     # ========== PAGES HTML ==========
    
    # Page d'accueil - Liste de tous les utilisateurs
    # path('', views.get_users, name='get_users'),
    
    # Ajouter un nouvel utilisateur
    path('users/add/', views.add_user_page, name='add_user_page'),
    
    # Créer l'utilisateur (traitement du formulaire)
    path('users/create/', views.create_user_form, name='create_user_form'),
    
    # Détails d'un utilisateur
    # path('users/<int:user_id>/', views.get_user_detail, name='user_detail'),
    
    # # Modifier les droits d'un utilisateur
    # path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    
    
    # ========== API ==========
    
    # Mettre à jour les permissions
#     path('api/users/<int:user_id>/permissions/', views.update_user_permissions, name='update_permissions'),
    
#     # Supprimer un utilisateur
#     path('api/users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    
#      # Recherche et gestion des étudiants
#     path('etudiants/recherche/', 
#          RechercheEtudiantView.as_view(), 
#          name='recherche_etudiant'),
    
#     path('etudiants/recherche-ajax/', 
#          recherche_rapide_etudiant_api, 
#          name='recherche_etudiant_ajax'),
    
#     path('etudiants/sync-api/', 
#          SyncEtudiantsAPIView.as_view(), 
#          name='sync_etudiants_api'),
    
#     # Création d'emprunt pour un étudiant
#     path('emprunts/creer/<int:etudiant_pk>/', 
#          creer_emprunt_etudiant, 
#          name='creer_emprunt_etudiant'),
    
    
    # Liste et recherche
    path('etudiants/', views.liste_etudiants, name='liste_etudiants'),
    
    # CRUD
    path('etudiants/ajouter/', views.ajouter_etudiant, name='ajouter_etudiant'),
    path('etudiants/<int:pk>/', views.etudiant_detail, name='etudiant_detail'),
    path('etudiants/<int:pk>/modifier/', views.modifier_etudiant, name='modifier_etudiant'),
    path('etudiants/<int:pk>/supprimer/', views.supprimer_etudiant, name='supprimer_etudiant'),
    
    # Synchronisation API
    path('etudiants/sync-api/', views.sync_etudiants_api, name='sync_etudiants_api'),
    
    # API JSON
    path('api/etudiants/', views.api_etudiants, name='api_etudiants'),
    path('api/etudiants/<int:pk>/', views.api_etudiant_detail, name='api_etudiant_detail'),

    
    # Détail d'un étudiant
    # path('etudiants/<int:pk>/', 
    #      Etudiant1DetailView.as_view(), 
    #      name='etudiant1_detail'),
    
     # ========== FACULTÉ ==========
    path('universites/<int:universite_pk>/facultes/ajouter/', views.faculte_create, name='faculte_create'),
    path('facultes/<int:pk>/modifier/', views.faculte_update, name='faculte_update'),
    path('facultes/<int:pk>/supprimer/', views.faculte_delete, name='faculte_delete'),
    
    # ========== DÉPARTEMENT ==========
    path('facultes/<int:faculte_pk>/departements/ajouter/', views.departement_create, name='departement_create'),
    path('departements/<int:pk>/modifier/', views.departement_update, name='departement_update'),
    path('departements/<int:pk>/supprimer/', views.departement_delete, name='departement_delete'),
    
    # ========== CLASSE ==========
    path('departements/<int:departement_pk>/classes/ajouter/', views.classe_create, name='classe_create'),
    path('classes/<int:pk>/', views.classe_detail, name='classe_detail'),
    path('classes/<int:pk>/modifier/', views.classe_update, name='classe_update'),
    path('classes/<int:pk>/supprimer/', views.classe_delete, name='classe_delete'),
    
    # ========== ÉTUDIANTS ==========
    path('etudiants/', views.liste_etudiants, name='liste_etudiants'),
    path('etudiants/ajouter/', views.ajouter_etudiant, name='ajouter_etudiant'),
    path('etudiants/<int:pk>/', views.etudiant_detail, name='detail_etudiant'),
    path('etudiants/<int:pk>/modifier/', views.modifier_etudiant, name='modifier_etudiant'),
    path('etudiants/<int:pk>/supprimer/', views.supprimer_etudiant, name='supprimer_etudiant'),
    
    
    path('api/get-facultes/', views.get_facultes, name='get_facultes'),
    path('api/get-departements/', views.get_departements, name='get_departements'),
    path('api/get-classes/', views.get_classes, name='get_classes'),
    path('api/get-niveaux/', views.get_niveaux, name='get_niveaux'),
    path('api/get-universites/', views.get_universites, name='get_universites'),
    path('api/get-all-donnees/', views.get_all_donnees_academiques, name='get_all_donnees_academiques'),
    
    
    
 # Inscription publique
    path('inscription/', views.inscription_etudiant, name='inscription_etudiant'),
    path('inscription/confirmation/', views.inscription_confirmation, name='inscription_confirmation'),
    
    # API pour chargement dynamique
    path('api/facultes/<int:universite_id>/', views.get_facultes_by_universite, name='get_facultes'),
    path('api/departements/<int:faculte_id>/', views.get_departements_by_faculte, name='get_departements'),
    path('api/classes/<int:departement_id>/', views.get_classes_by_departement, name='get_classes'),



]
