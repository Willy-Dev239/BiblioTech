# bibliotheque/views.py

import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import timedelta
from django.contrib.auth.hashers import make_password
import json
from django.db.models import Count, Sum, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from .models import (
    ParametreBibliotheque, CategorieEmprunteur, JourFerie,
    MessageSysteme, RegleMetier, ConfigurationEmail, HistoriqueParametres
)
from .forms import (
    ParametreBibliothequeForm, CategorieEmprunteurForm, JourFerieForm,
    MessageSystemeForm, RegleMetierForm, ConfigurationEmailForm
)


from django.views.generic import CreateView, ListView, DetailView
from django.urls import reverse_lazy

from .models import Etudiant1, Emprunt, Livre
from .forms import EmpruntForm, RechercheEtudiantForm
from .forms import InscriptionEtudiantForm



from django.db.models import Q
from .models import Etudiant, Abonnement, Universite, Auteur
from .forms import EtudiantForm, AbonnementForm, UniversiteForm, AuteurForm


from .models import (
    Universite, Auteur, Etagere, Compartiment, EmplacementLivre,
    Livre, Personnel, Etudiant, Abonnement, Emprunt, Reservation, Notification
)
from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm, CustomPasswordChangeForm,
    UniversiteForm, AuteurForm, EtagereForm, CompartimentForm, EmplacementLivreForm,
    LivreForm, PersonnelForm, EtudiantForm, AbonnementForm, EmpruntForm,
    ReservationForm, NotificationForm, RechercherLivreForm, RechercherEtudiantForm
)
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import json
from datetime import datetime
from django.http import JsonResponse, HttpResponseNotAllowed


# ==========configuration mail==============
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bibliotheque.settings')
django.setup()

from django.core.mail import send_mail




# ==================== VUES D'AUTHENTIFICATION ====================

def register_view(request):
    """Vue d'inscription"""
    
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Votre compte a été créé avec succès!')
            return render(request, "bibliotheque/auth/login.html")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'bibliotheque/auth/register.html', {'form': form})


def login_view(request):
    """Vue de connexion"""
    # if request.user.is_authenticated:
    #     return redirect('home')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)
                messages.success(request, f'Bienvenue {user.username}!')
                return redirect('home')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'bibliotheque/auth/login.html', {'form': form})


def logout_view(request):
    """Vue de déconnexion"""
    logout(request)
    messages.info(request, 'Vous êtes déconnecté.')
    return redirect('login')


@login_required
def change_password_view(request):
    """Vue de changement de mot de passe"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Votre mot de passe a été changé avec succès!')
            return redirect('login')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'bibliotheque/auth/change_password.html', {'form': form})


# ==================== VUES GÉNÉRALES ====================

@login_required
def dashboard_home(request):
    """Vue principale du dashboard avec statistiques"""
    
    today = timezone.now().date()
    
    # Statistiques générales
    total_etudiants = Etudiant.objects.filter(actif=True).count()
    total_abonnements = Abonnement.objects.filter(actif=True).count()
    total_universites = Universite.objects.filter(actif=True).count()
    total_auteurs = Auteur.objects.count()
    
    # Statistiques des livres (à adapter selon votre modèle Livre)
    # total_livres = Livre.objects.count()
    # emprunts_actifs = Emprunt.objects.filter(date_retour__isnull=True).count()
    # emprunts_retard = Emprunt.objects.filter(
    #     date_retour__isnull=True,
    #     date_retour_prevue__lt=today
    # ).count()
    
    # Valeurs par défaut si les modèles Livre/Emprunt n'existent pas encore
    total_livres = 0
    emprunts_actifs = 0
    emprunts_retard = 0
    
    # Revenus du mois (somme des montants d'abonnements du mois en cours)
    premier_jour_mois = today.replace(day=1)
    revenus_mois = Abonnement.objects.filter(
        date_debut__gte=premier_jour_mois,
        date_debut__lte=today
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    # Activités récentes (derniers 10 étudiants inscrits)
    activites_recentes = []
    derniers_etudiants = Etudiant.objects.select_related('universite').order_by('-annee_inscription')[:10]
    
    for etudiant in derniers_etudiants:
        activites_recentes.append({
            'date': etudiant.annee_inscription,
            'type': 'inscription',
            'etudiant': etudiant,
            'livre': None,
            'statut': 'actif' if etudiant.actif else 'inactif',
            'date_retour': None
        })
    
    # Statistiques pour les graphiques
    
    # Emprunts par mois (12 derniers mois) - données factices pour l'exemple
    emprunts_par_mois = [12, 19, 15, 25, 22, 30, 28, 35, 32, 38, 40, 45]
    
    # Répartition des étudiants par niveau
    etudiants_par_niveau_data = Etudiant.objects.values('niveau').annotate(
        count=Count('id')
    ).order_by('niveau')
    
    # Préparer les données pour le graphique
    niveaux_count = [0, 0, 0, 0, 0]  # L1, L2, L3, M, D
    for item in etudiants_par_niveau_data:
        niveau = item['niveau']
        count = item['count']
        if niveau == 'L1':
            niveaux_count[0] = count
        elif niveau == 'L2':
            niveaux_count[1] = count
        elif niveau == 'L3':
            niveaux_count[2] = count
        elif niveau == 'M':
            niveaux_count[3] = count
        elif niveau == 'D':
            niveaux_count[4] = count
    
    etudiants_par_niveau = json.dumps(niveaux_count)
    
    context = {
        'today': today,
        'total_etudiants': total_etudiants,
        'total_abonnements': total_abonnements,
        'total_livres': total_livres,
        'emprunts_actifs': emprunts_actifs,
        'total_universites': total_universites,
        'total_auteurs': total_auteurs,
        'emprunts_retard': emprunts_retard,
        'revenus_mois': revenus_mois,
        'activites_recentes': activites_recentes,
        'emprunts_par_mois': json.dumps(emprunts_par_mois),
        'etudiants_par_niveau': etudiants_par_niveau,
    }
    
    return render(request, 'bibliotheque/home.html', context)


@login_required
def dashboard_statistics(request):
    """Vue pour obtenir des statistiques détaillées en JSON (pour AJAX)"""
    
    today = timezone.now().date()
    
    # Statistiques par université
    stats_universites = Universite.objects.annotate(
        nb_etudiants=Count('etudiants')
    ).values('nom', 'nb_etudiants').order_by('-nb_etudiants')[:5]
    
    # Top 5 universités
    top_universites = {
        'labels': [u['nom'] for u in stats_universites],
        'data': [u['nb_etudiants'] for u in stats_universites]
    }
    
    # Évolution des inscriptions (30 derniers jours)
    derniers_30_jours = today - timedelta(days=30)
    inscriptions_par_jour = []
    
    for i in range(30):
        jour = derniers_30_jours + timedelta(days=i)
        count = Etudiant.objects.filter(
            date_inscription__date=jour
        ).count()
        inscriptions_par_jour.append({
            'date': jour.strftime('%d/%m'),
            'count': count
        })
    
    # Taux d'abonnements actifs
    total_etudiants = Etudiant.objects.count()
    etudiants_avec_abo = Etudiant.objects.filter(
        abonnements__actif=True
    ).distinct().count()
    
    taux_abonnement = (etudiants_avec_abo / total_etudiants * 100) if total_etudiants > 0 else 0
    
    data = {
        'top_universites': top_universites,
        'inscriptions_evolution': inscriptions_par_jour,
        'taux_abonnement': round(taux_abonnement, 2),
        'timestamp': timezone.now().isoformat()
    }
    
    from django.http import JsonResponse
    return JsonResponse(data)


@login_required
def export_statistics(request):
    """Exporter les statistiques en CSV ou Excel"""
   
    
    format_type = request.GET.get('format', 'csv')
    
    if format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="statistiques_bibliotheque.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Statistique', 'Valeur'])
        
        # Écrire les statistiques
        writer.writerow(['Total Étudiants', Etudiant.objects.count()])
        writer.writerow(['Étudiants Actifs', Etudiant.objects.filter(actif=True).count()])
        writer.writerow(['Total Abonnements', Abonnement.objects.count()])
        writer.writerow(['Abonnements Actifs', Abonnement.objects.filter(actif=True).count()])
        writer.writerow(['Total Universités', Universite.objects.count()])
        writer.writerow(['Total Auteurs', Auteur.objects.count()])
        
        return response
    
    # Pour Excel, vous pouvez utiliser openpyxl ou xlsxwriter
    # (nécessite l'installation de la bibliothèque)

@login_required
def home_view(request):
    """Page d'accueil"""
    context = {
        'total_livres': Livre.objects.count(),
        'livres_disponibles': Livre.objects.filter(disponible=True).count(),
        'total_etudiants': Etudiant.objects.filter(actif=True).count(),
        'emprunts_actifs': Emprunt.objects.filter(statut='EN_COURS').count(),
        'emprunts_retard': Emprunt.objects.filter(statut='EN_RETARD').count(),
        'derniers_livres': Livre.objects.all()[:5],
        'emprunts_recents': Emprunt.objects.select_related('livre', 'etudiant')[:10],
    }
    
    # Si l'utilisateur est un étudiant
    if hasattr(request.user, 'etudiant'):
        etudiant = request.user.etudiant
        context['mes_emprunts'] = etudiant.emprunts.filter(date_retour_effective__isnull=True)
        context['mes_reservations'] = etudiant.reservations.exclude(statut__in=['ANNULEE', 'EXPIREE'])
        context['mes_notifications'] = etudiant.notifications.filter(lu=False)[:5]
    
    return render(request, 'bibliotheque/home.html', context)


# ==================== VUES LIVRES ====================



@login_required
def livre_list_view(request):
    """Liste des livres avec recherche"""
    form = RechercherLivreForm(request.GET)
    livres = Livre.objects.all().prefetch_related('auteurs')
    
    if form.is_valid():
        recherche = form.cleaned_data.get('recherche')
        categorie = form.cleaned_data.get('categorie')
        langue = form.cleaned_data.get('langue')
        disponible = form.cleaned_data.get('disponible')
        
        if recherche:
            livres = livres.filter(
                Q(titre__icontains=recherche) |
                Q(isbn__icontains=recherche) |
                Q(auteurs__nom__icontains=recherche) |
                Q(auteurs__prenom__icontains=recherche)
            ).distinct()
        
        if categorie:
            livres = livres.filter(categorie__icontains=categorie)
        
        if langue:
            livres = livres.filter(langue=langue)
        
        if disponible:
            livres = livres.filter(disponible=True)
    
    paginator = Paginator(livres, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'total_livres': livres.count()
    }
    return render(request, 'bibliotheque/livres/liste.html', context)

@login_required
def livre_detail_view(request, pk):
    """Détail d'un livre"""
    livre = get_object_or_404(Livre.objects.prefetch_related('auteurs'), pk=pk)
    peut_reserver = False
    
    if request.user.is_authenticated and hasattr(request.user, 'etudiant'):
        etudiant = request.user.etudiant
        peut_reserver = (
            livre.exemplaires_disponibles == 0 and
            etudiant.a_abonnement_actif and
            not livre.reservations.filter(etudiant=etudiant, statut='EN_ATTENTE').exists()
        )
    
    context = {
        'livre': livre,
        'peut_reserver': peut_reserver,
        'emprunts_historique': livre.emprunts.select_related('etudiant')[:5]
    }
    return render(request, 'bibliotheque/livres/detail.html', context)


@login_required
def livre_create_view(request):
    """Créer un livre"""
    if request.method == 'POST':
        form = LivreForm(request.POST, request.FILES)
        if form.is_valid():
            livre = form.save()
            messages.success(request, f'Le livre "{livre.titre}" a été ajouté avec succès!')
            return redirect('livre_detail', pk=livre.pk)
    else:
        form = LivreForm()
    
    return render(request, 'bibliotheque/livres/form.html', {'form': form, 'action': 'Ajouter'})


@login_required
def livre_update_view(request, pk):
    """Modifier un livre"""
    livre = get_object_or_404(Livre, pk=pk)
    
    if request.method == 'POST':
        form = LivreForm(request.POST, request.FILES, instance=livre)
        if form.is_valid():
            livre = form.save()
            messages.success(request, f'Le livre "{livre.titre}" a été modifié avec succès!')
            return redirect('livre_detail', pk=livre.pk)
    else:
        form = LivreForm(instance=livre)
    
    return render(request, 'bibliotheque/livres/form.html', {
        'form': form,
        'livre': livre,
        'action': 'Modifier'
    })


@login_required
def livre_delete_view(request, pk):
    """Supprimer un livre"""
    livre = get_object_or_404(Livre, pk=pk)
    
    if request.method == 'POST':
        titre = livre.titre
        livre.delete()
        messages.success(request, f'Le livre "{titre}" a été supprimé.')
        return redirect('livre_list')
    
    return render(request, 'bibliotheque/livres/delete.html', {'livre': livre})


# ==================== VUES ÉTUDIANTS ====================


@login_required
def abonnes(request):
    """
    Vue pour lister tous les abonnés (étudiants)
    """
    # Récupérer tous les étudiants avec leurs relations
    etudiants = Etudiant.objects.all().select_related('universite').order_by('nom', 'prenom')
    
    # Recherche
    search = request.GET.get('search')
    if search:
        etudiants = etudiants.filter(
            Q(nom__icontains=search) |
            Q(prenom__icontains=search) |
            Q(email__icontains=search) |
            Q(telephone__icontains=search)
        )
    
    # Filtre par université
    universite_id = request.GET.get('universite')
    if universite_id:
        etudiants = etudiants.filter(universite_id=universite_id)
    
    # Annoter avec le nombre d'emprunts actifs
    etudiants = etudiants.annotate(
        emprunts_actifs=Count('emprunts', filter=Q(emprunts__date_retour_effective__isnull=True))
    )
    
    # Liste des universités pour le filtre
    universites = Universite.objects.all()
    
    context = {
        'etudiants': etudiants,
        'universites': universites,
        'search': search,
        'universite_filtre': universite_id,
    }
    
    return render(request, 'bibliotheque/abonnements/abonnement_list.html', context)




@login_required
def abonne_detail(request, pk):
    """
    Vue pour afficher les détails d'un abonné
    """
    etudiant = get_object_or_404(Etudiant, pk=pk)
    
    # Récupérer les emprunts de l'étudiant
    emprunts_actifs = Emprunt.objects.filter(
        etudiant=etudiant,
        date_retour_effective__isnull=True
    ).select_related('livre', 'livre__auteur').order_by('-date_emprunt')
    
    emprunts_historique = Emprunt.objects.filter(
        etudiant=etudiant,
        date_retour_effective__isnull=False
    ).select_related('livre', 'livre__auteur').order_by('-date_retour_effective')[:10]
    
    # Récupérer les abonnements
    abonnements = Abonnement.objects.filter(etudiant=etudiant).order_by('-annee_inscription')
    
    # Calculer les statistiques
    total_emprunts = Emprunt.objects.filter(etudiant=etudiant).count()
    emprunts_en_cours = emprunts_actifs.count()
    
    # Emprunts en retard
    aujourd_hui = timezone.now().date()
    emprunts_retard = emprunts_actifs.filter(date_retour_prevue__lt=aujourd_hui).count()
    
    # Calculer les pénalités
    penalites_total = 0
    for emprunt in emprunts_actifs:
        if emprunt.date_retour_prevue < aujourd_hui:
            jours_retard = (aujourd_hui - emprunt.date_retour_prevue).days
            penalites_total += jours_retard * 500  # 500 BIF par jour
    
    context = {
        'etudiant': etudiant,
        'emprunts_actifs': emprunts_actifs,
        'emprunts_historique': emprunts_historique,
        'abonnements': abonnements,
        'total_emprunts': total_emprunts,
        'emprunts_en_cours': emprunts_en_cours,
        'emprunts_retard': emprunts_retard,
        'penalites_total': penalites_total,
    }
    
    return render(request, 'bibliotheque/abonnements/abonne_detail.html', context)

@login_required
def abonne_create(request):
    """
    Vue pour créer un nouvel abonné
    """
    if request.method == 'POST':
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        adresse = request.POST.get('adresse')
        universite_id = request.POST.get('universite')
        date_naissance = request.POST.get('date_naissance')
        
        try:
            universite = Universite.objects.get(pk=universite_id)
            
            # Créer l'étudiant
            etudiant = Etudiant.objects.create(
                nom=nom,
                prenom=prenom,
                email=email,
                telephone=telephone,
                adresse=adresse,
                universite=universite,
                date_naissance=date_naissance if date_naissance else None
            )
            
            messages.success(request, f'Abonné {nom} {prenom} créé avec succès.')
            return redirect('abonne_detail', pk=etudiant.pk)
            
        except Universite.DoesNotExist:
            messages.error(request, 'Université introuvable.')
            return redirect('abonne_create')
        except Exception as e:
            messages.error(request, f'Erreur lors de la création: {str(e)}')
            return redirect('abonne_create')
    
    # GET request
    universites = Universite.objects.all().order_by('nom')
    
    context = {
        'universites': universites,
    }
    
    return render(request, 'bibliotheque/abonnements/abonne_create.html', context)

@login_required
def abonne_edit(request, pk):
    """
    Vue pour modifier un abonné existant
    """
    etudiant = get_object_or_404(Etudiant, pk=pk)
    
    if request.method == 'POST':
        etudiant.nom = request.POST.get('nom')
        etudiant.prenom = request.POST.get('prenom')
        etudiant.email = request.POST.get('email')
        etudiant.telephone = request.POST.get('telephone')
        etudiant.adresse = request.POST.get('adresse')
        
        universite_id = request.POST.get('universite')
        date_naissance = request.POST.get('date_naissance')
        
        try:
            if universite_id:
                etudiant.universite = Universite.objects.get(pk=universite_id)
            
            if date_naissance:
                etudiant.date_naissance = date_naissance
            
            etudiant.save()
            
            messages.success(request, f'Abonné {etudiant.nom} {etudiant.prenom} modifié avec succès.')
            return redirect('abonne_detail', pk=etudiant.pk)
            
        except Universite.DoesNotExist:
            messages.error(request, 'Université introuvable.')
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification: {str(e)}')
    
    # GET request
    universites = Universite.objects.all().order_by('nom')
    
    context = {
        'etudiant': etudiant,
        'universites': universites,
    }
    
    return render(request, 'bibliotheque/abonnements/abonne_edit.html', context)

@login_required
def abonne_delete(request, pk):
    """
    Vue pour supprimer un abonné
    """
    etudiant = get_object_or_404(Etudiant, pk=pk)
    
    # Vérifier s'il y a des emprunts actifs
    emprunts_actifs = Emprunt.objects.filter(
        etudiant=etudiant,
        date_retour_effective__isnull=True
    ).count()
    
    if request.method == 'POST':
        if emprunts_actifs > 0:
            messages.error(
                request, 
                f'Impossible de supprimer {etudiant.nom} {etudiant.prenom}. '
                f'Il/Elle a {emprunts_actifs} emprunt(s) actif(s).'
            )
            return redirect('abonne_detail', pk=pk)
        
        nom_complet = f"{etudiant.nom} {etudiant.prenom}"
        etudiant.delete()
        
        messages.success(request, f'Abonné {nom_complet} supprimé avec succès.')
        return redirect('abonnes')
    
    context = {
        'etudiant': etudiant,
        'emprunts_actifs': emprunts_actifs,
    }
    
    return render(request, 'bibliotheque/abonnements/abonne_delete.html', context)

@login_required
def abonne_emprunts(request, pk):
    """
    Vue pour afficher tous les emprunts d'un abonné
    """
    etudiant = get_object_or_404(Etudiant, pk=pk)
    
    # Filtrer par statut
    statut = request.GET.get('statut', 'tous')
    
    emprunts = Emprunt.objects.filter(etudiant=etudiant).select_related('livre', 'livre__auteur')
    
    if statut == 'actif':
        emprunts = emprunts.filter(date_retour_effective__isnull=True)
    elif statut == 'retourne':
        emprunts = emprunts.filter(date_retour_effective__isnull=False)
    elif statut == 'retard':
        aujourd_hui = timezone.now().date()
        emprunts = emprunts.filter(
            date_retour_prevue__lt=aujourd_hui,
            date_retour_effective__isnull=True
        )
    
    emprunts = emprunts.order_by('-date_emprunt')
    
    context = {
        'etudiant': etudiant,
        'emprunts': emprunts,
        'statut_filtre': statut,
    }
    
    return render(request, 'bibliotheque/abonnements/abonne_emprunts.html', context)



@login_required
def etudiant_list_view(request):
    """Liste des étudiants avec recherche"""
    form = RechercherEtudiantForm(request.GET)
    etudiants = Etudiant.objects.all().select_related('universite')
    stdents = Etudiant.objects.all()
    
    if form.is_valid():
        recherche = form.cleaned_data.get('recherche')
        universite = form.cleaned_data.get('universite')
        niveau = form.cleaned_data.get('niveau')
        actif = form.cleaned_data.get('actif')
        
        if recherche:
            etudiants = etudiants.filter(
                Q(nom__icontains=recherche) |
                Q(prenom__icontains=recherche) |
                Q(numero_etudiant__icontains=recherche) |
                Q(email__icontains=recherche)
            )
        
        if universite:
            etudiants = etudiants.filter(universite=universite)
        
        if niveau:
            etudiants = etudiants.filter(niveau=niveau)
        
        if actif:
            etudiants = etudiants.filter(actif=True)
    
    paginator = Paginator(etudiants, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'stdents':stdents,
        'total_etudiants': etudiants.count()
    }
    return render(request, 'bibliotheque/etudiants/liste.html', context)


@login_required
def etudiant_detail_view(request, pk):
    """Détail d'un étudiant"""
    etudiant = get_object_or_404(Etudiant.objects.select_related('universite'), pk=pk)
    stdents = Etudiant.objects.all()
    
    context = {
        'etudiant': etudiant,
        'stdents': stdents,
        'abonnement_actif': etudiant.abonnements.filter(actif=True).first(),
        'emprunts_actifs': etudiant.emprunts.filter(date_retour_effective__isnull=True),
        'historique_emprunts': etudiant.emprunts.all()[:10],
        'reservations': etudiant.reservations.exclude(statut__in=['ANNULEE', 'EXPIREE']),
    }
    return render(request, 'bibliotheque/etudiants/detail.html', context)


@login_required
def etudiant_create_view(request):
    """Créer un étudiant"""
    if request.method == 'POST':
        form = EtudiantForm(request.POST, request.FILES)
        if form.is_valid():
            etudiant = form.save()
            messages.success(request, f'L\'étudiant {etudiant.nom} {etudiant.prenom} a été ajouté!')
            return redirect('abonnes')
    else:
        form = EtudiantForm()
    
    return render(request, 'bibliotheque/etudiants/form.html', {'form': form, 'action': 'Ajouter'})


@login_required
def etudiant_update_view(request, pk):
    """Modifier un étudiant"""
    etudiant = get_object_or_404(Etudiant, pk=pk)
    
    if request.method == 'POST':
        form = EtudiantForm(request.POST, request.FILES, instance=etudiant)
        if form.is_valid():
            etudiant = form.save()
            messages.success(request, f'L\'étudiant {etudiant.nom} a été modifié!')
            return redirect('abonnes')
    else:
        form = EtudiantForm(instance=etudiant)
    
    return render(request, 'bibliotheque/etudiants/form.html', {
        'form': form,
        'etudiant': etudiant,
        'action': 'Modifier'
    })


# ==================== VUES EMPRUNTS ====================


@login_required
def emprunt_detail(request, pk):
    """
    Vue pour afficher les détails d'un emprunt
    """
    emprunt = get_object_or_404(Emprunt, pk=pk)
    
    # Calculer les informations supplémentaires
    jours_restants = None
    est_en_retard = False
    jours_retard = 0
    
    if emprunt.date_retour_prevue:
        aujourd_hui = timezone.now().date()
        difference = (emprunt.date_retour_prevue - aujourd_hui).days
        
        if difference < 0:
            est_en_retard = True
            jours_retard = abs(difference)
        else:
            jours_restants = difference
    
    # Calculer les pénalités si en retard
    penalite = 0
    if est_en_retard and jours_retard > 0:
        # Exemple : 500 BIF par jour de retard
        penalite = jours_retard * 500
    
    context = {
        'emprunt': emprunt,
        'jours_restants': jours_restants,
        'est_en_retard': est_en_retard,
        'jours_retard': jours_retard,
        'penalite': penalite,
    }
    
    return render(request, 'bibliotheque/emprunts/emprunt_detail.html', context)

@login_required
def emprunt_list_view(request):
    """Liste des emprunts"""
    emprunts = Emprunt.objects.all().select_related('livre', 'etudiant', 'personnel')
    emprunt = Emprunt.objects.all()
    
    statut = request.GET.get('statut')
    if statut:
        emprunts = emprunts.filter(statut=statut)
    
    paginator = Paginator(emprunts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'emprunt':emprunt,
        'statuts': Emprunt.STATUTS,
        'statut_selectionne': statut
    }
    return render(request, 'bibliotheque/emprunts/liste.html', context)


@login_required
def emprunt_create_view(request):
    """Créer un emprunt"""
    if request.method == 'POST':
        form = EmpruntForm(request.POST)
        if form.is_valid():
            emprunt = form.save(commit=False)
            if hasattr(request.user, 'personnel'):
                emprunt.personnel = request.user.personnel
            emprunt.save()
            
            # Mettre à jour la disponibilité du livre
            livre = emprunt.livre
            if livre.exemplaires_disponibles <= 0:
                livre.disponible = False
                livre.save()
            
            messages.success(request, 'L\'emprunt a été créé avec succès!')
            return redirect('emprunt_list')
    else:
        form = EmpruntForm()
    
    return render(request, 'bibliotheque/emprunts/form.html', {'form': form, 'action': 'Créer'})


@login_required
def emprunt_retour_view(request, pk):
    """Retour d'un emprunt"""
    emprunt = get_object_or_404(Emprunt, pk=pk)
    
    if request.method == 'POST':
        emprunt.date_retour_effective = timezone.now().date()
        emprunt.statut = 'RETOURNE'
        
        # Calculer la pénalité si retard
        if emprunt.est_en_retard:
            jours_retard = emprunt.jours_retard
            emprunt.penalite = jours_retard * 500  # 500 par jour de retard
        
        emprunt.save()
        
        # Mettre à jour la disponibilité du livre
        livre = emprunt.livre
        if livre.exemplaires_disponibles > 0:
            livre.disponible = True
            livre.save()
        
        messages.success(request, 'Le retour a été enregistré avec succès!')
        return redirect('emprunt_list')
    
    return render(request, 'bibliotheque/emprunts/retour.html', {'emprunt': emprunt})


# ==================== VUES RÉSERVATIONS ====================

@login_required
def reservation_create_view(request, livre_pk):
    """Créer une réservation"""
    livre = get_object_or_404(Livre, pk=livre_pk)
    
    if not hasattr(request.user, 'etudiant'):
        messages.error(request, 'Seuls les étudiants peuvent réserver des livres.')
        return redirect('livre_detail', pk=livre_pk)
    
    etudiant = request.user.etudiant
    
    if not etudiant.a_abonnement_actif:
        messages.error(request, 'Vous devez avoir un abonnement actif pour réserver.')
        return redirect('livre_detail', pk=livre_pk)
    
    if livre.exemplaires_disponibles > 0:
        messages.info(request, 'Ce livre est disponible, vous pouvez l\'emprunter directement.')
        return redirect('livre_detail', pk=livre_pk)
    
    # Vérifier si déjà réservé
    if livre.reservations.filter(etudiant=etudiant, statut='EN_ATTENTE').exists():
        messages.warning(request, 'Vous avez déjà réservé ce livre.')
        return redirect('livre_detail', pk=livre_pk)
    
    if request.method == 'POST':
        reservation = Reservation.objects.create(
            livre=livre,
            etudiant=etudiant,
            date_expiration=timezone.now().date() + timedelta(days=3),
            statut='EN_ATTENTE'
        )
        messages.success(request, 'Votre réservation a été enregistrée!')
        return redirect('livre_detail', pk=livre_pk)
    
    return render(request, 'bibliotheque/reservations/confirmer.html', {'livre': livre})


@login_required
def reservation_annuler_view(request, pk):
    """Annuler une réservation"""
    reservation = get_object_or_404(Reservation, pk=pk)
    
    if hasattr(request.user, 'etudiant') and reservation.etudiant != request.user.etudiant:
        messages.error(request, 'Vous ne pouvez annuler que vos propres réservations.')
        return redirect('home')
    
    if request.method == 'POST':
        reservation.statut = 'ANNULEE'
        reservation.save()
        messages.success(request, 'Votre réservation a été annulée.')
        return redirect('home')
    
    return render(request, 'bibliotheque/reservations/annuler.html', {'reservation': reservation})


# ==================== VUES ABONNEMENTS ====================

@login_required
def abonnement_create_view(request, etudiant_pk):
    """Créer un abonnement"""
    etudiant = get_object_or_404(Etudiant, pk=etudiant_pk)
    
    if request.method == 'POST':
        form = AbonnementForm(request.POST)
        if form.is_valid():
            abonnement = form.save()
            messages.success(request, 'L\'abonnement a été créé avec succès!')
            return redirect('etudiant_detail', pk=etudiant_pk)
    else:
        form = AbonnementForm(initial={'etudiant': etudiant})
    
    return render(request, 'bibliotheque/abonnements/form.html', {
        'form': form,
        'etudiant': etudiant,
        'action': 'Créer'
    })


# ==================== VUES NOTIFICATIONS ====================

@login_required
def notification_list_view(request):
    """Liste des notifications de l'étudiant"""
    if not hasattr(request.user, 'etudiant'):
        messages.error(request, 'Cette page est réservée aux étudiants.')
        return redirect('home')
    
    etudiant = request.user.etudiant
    notifications = etudiant.notifications.all()
    
    # Marquer comme lues
    notifications.filter(lu=False).update(lu=True)
    
    context = {'notifications': notifications}
    return render(request, 'bibliotheque/notifications/liste.html', context)

# ========== VUES ÉTAGÈRES ==========

@login_required
def etagere_list_view(request):
    """Liste des étagères"""
    search_query = request.GET.get('search', '')
    salle_filter = request.GET.get('salle', '')
    etage_filter = request.GET.get('etage', '')
    
    etageres = Etagere.objects.annotate(
        nb_compartiments=Count('compartiments'),
        nb_emplacements=Count('compartiments__emplacements')
    )
    
    if search_query:
        etageres = etageres.filter(
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(salle__icontains=search_query)
        )
    
    if salle_filter:
        etageres = etageres.filter(salle=salle_filter)
    
    if etage_filter:
        etageres = etageres.filter(etage=etage_filter)
    
    etageres = etageres.order_by('salle', 'etage', 'code')
    
    # Pour les filtres
    salles = Etagere.objects.values_list('salle', flat=True).distinct()
    etages = Etagere.objects.values_list('etage', flat=True).distinct().order_by('etage')
    
    context = {
        'etageres': etageres,
        'search_query': search_query,
        'salles': salles,
        'etages': etages,
        'salle_filter': salle_filter,
        'etage_filter': etage_filter,
    }
    return render(request, 'bibliotheque/etageres/liste.html', context)


@login_required
def etagere_detail_view(request, pk):
    """Détail d'une étagère"""
    etagere = get_object_or_404(Etagere, pk=pk)
    compartiments = etagere.compartiments.annotate(
        nb_emplacements=Count('emplacements'),
        nb_emplacements_occupes=Count('emplacements', filter=Q(emplacements__disponible=False))
    ).order_by('niveau', 'numero')
    
    context = {
        'etagere': etagere,
        'compartiments': compartiments,
        # 'taux_remplissage': etagere.taux_remplissage(),
    }
    return render(request, 'bibliotheque/etageres/detail.html', context)


@login_required
def etagere_create_view(request):
    """Création d'une étagère"""
    if request.method == 'POST':
        form = EtagereForm(request.POST)
        if form.is_valid():
            etagere = form.save()
            messages.success(request, f"L'étagère {etagere.code} a été créée avec succès.")
            return redirect('etagere_detail', pk=etagere.pk)
    else:
        form = EtagereForm()
    
    context = {'form': form, 'action': 'Créer'}
    return render(request, 'bibliotheque/etageres/form.html', context)


@login_required
def etagere_update_view(request, pk):
    """Modification d'une étagère"""
    etagere = get_object_or_404(Etagere, pk=pk)
    
    if request.method == 'POST':
        form = EtagereForm(request.POST, instance=etagere)
        if form.is_valid():
            form.save()
            messages.success(request, f"L'étagère {etagere.code} a été modifiée avec succès.")
            return redirect('bibliotheque:etagere_detail', pk=etagere.pk)
    else:
        form = EtagereForm(instance=etagere)
    
    context = {'form': form, 'etagere': etagere, 'action': 'Modifier'}
    return render(request, 'bibliotheque/etageres/form.html', context)


@login_required
def etagere_delete_view(request, pk):
    """Suppression d'une étagère"""
    etagere = get_object_or_404(Etagere, pk=pk)
    
    if request.method == 'POST':
        code = etagere.code
        etagere.delete()
        messages.success(request, f"L'étagère {code} a été supprimée avec succès.")
        return redirect('bibliotheque:etagere_list')
    
    context = {'etagere': etagere}
    return render(request, 'bibliotheque/etageres/delete.html', context)


# ========== VUES COMPARTIMENTS ==========

@login_required
def compartiment_list_view(request):
    """Liste des compartiments"""
    search_query = request.GET.get('search', '')
    etagere_filter = request.GET.get('etagere', '')
    categorie_filter = request.GET.get('categorie', '')
    
    compartiments = Compartiment.objects.select_related('etagere').annotate(
        nb_emplacements=Count('emplacements'),
        nb_emplacements_occupes=Count('emplacements', filter=Q(emplacements__disponible=False))
    )
    
    if search_query:
        compartiments = compartiments.filter(
            Q(etagere__code__icontains=search_query) |
            Q(niveau__icontains=search_query) |
            Q(categorie__icontains=search_query)
        )
    
    if etagere_filter:
        compartiments = compartiments.filter(etagere_id=etagere_filter)
    
    if categorie_filter:
        compartiments = compartiments.filter(categorie=categorie_filter)
    
    compartiments = compartiments.order_by('etagere__code', 'niveau', 'numero')
    
    # Pour les filtres
    etageres = Etagere.objects.all().order_by('code')
    categories = Compartiment.objects.values_list('categorie', flat=True).distinct()
    
    context = {
        'compartiments': compartiments,
        'search_query': search_query,
        'etageres': etageres,
        'categories': categories,
        'etagere_filter': etagere_filter,
        'categorie_filter': categorie_filter,
    }
    return render(request, 'bibliotheque/compartiments/liste.html', context)


@login_required
def compartiment_detail_view(request, pk):
    """Détail d'un compartiment"""
    compartiment = get_object_or_404(
        Compartiment.objects.select_related('etagere'),
        pk=pk
    )
    emplacements = compartiment.emplacements.select_related('livre').order_by('position')
    
    context = {
        'compartiment': compartiment,
        'emplacements': emplacements,
        # 'taux_occupation': compartiment.taux_occupation(),
    }
    return render(request, 'bibliotheque/compartiments/detail.html', context)


@login_required
def compartiment_create_view(request):
    """Création d'un compartiment"""
    etagere_id = request.GET.get('etagere')
    
    if request.method == 'POST':
        form = CompartimentForm(request.POST)
        if form.is_valid():
            compartiment = form.save()
            messages.success(request, f"Le compartiment {compartiment} a été créé avec succès.")
            return redirect('compartiment_detail', pk=compartiment.pk)
    else:
        initial = {}
        if etagere_id:
            initial['etagere'] = etagere_id
        form = CompartimentForm(initial=initial)
    
    context = {'form': form, 'action': 'Créer'}
    return render(request, 'bibliotheque/compartiments/form.html', context)


@login_required
def compartiment_update_view(request, pk):
    """Modification d'un compartiment"""
    compartiment = get_object_or_404(Compartiment, pk=pk)
    
    if request.method == 'POST':
        form = CompartimentForm(request.POST, instance=compartiment)
        if form.is_valid():
            form.save()
            messages.success(request, f"Le compartiment {compartiment} a été modifié avec succès.")
            return redirect('bibliotheque:compartiment_detail', pk=compartiment.pk)
    else:
        form = CompartimentForm(instance=compartiment)
    
    context = {'form': form, 'compartiment': compartiment, 'action': 'Modifier'}
    return render(request, 'bibliotheque/compartiments/form.html', context)


@login_required
def compartiment_delete_view(request, pk):
    """Suppression d'un compartiment"""
    compartiment = get_object_or_404(Compartiment, pk=pk)
    
    if request.method == 'POST':
        etagere = compartiment.etagere
        compartiment.delete()
        messages.success(request, f"Le compartiment a été supprimé avec succès.")
        return redirect('bibliotheque:etagere_detail', pk=etagere.pk)
    
    context = {'compartiment': compartiment}
    return render(request, 'bibliotheque/compartiments/delete.html', context)


# ========== VUES EMPLACEMENTS ==========

@login_required
def emplacement_list_view(request):
    """Liste des emplacements"""
    search_query = request.GET.get('search', '')
    disponible_filter = request.GET.get('disponible', '')
    compartiment_filter = request.GET.get('compartiment', '')
    
    
    emplacements = EmplacementLivre.objects.select_related(
        'compartiment__etagere', 'livre'
    )
    
    if search_query:
        emplacements = emplacements.filter(
            Q(code_emplacement__icontains=search_query) |
            Q(compartiment__etagere__code__icontains=search_query) |
            Q(livre__titre__icontains=search_query)
        )
    
    if disponible_filter == 'oui':
        emplacements = emplacements.filter(disponible=True)
    elif disponible_filter == 'non':
        emplacements = emplacements.filter(disponible=False)
    
    if compartiment_filter:
        emplacements = emplacements.filter(compartiment_id=compartiment_filter)
    
    emplacements = emplacements.order_by(
        'compartiment__etagere__code',
        'compartiment__niveau',
        'compartiment__numero',
        'position'
    )
    
    # Pour les filtres
    compartiments = Compartiment.objects.select_related('etagere').order_by('etagere__code', 'numero')
    emplacment = EmplacementLivre.objects.all()
    
    context = {
        'emplacements': emplacements,
        'emplacment':emplacment,
        'search_query': search_query,
        'compartiments': compartiments,
        'disponible_filter': disponible_filter,
        'compartiment_filter': compartiment_filter,
    }
    return render(request, 'bibliotheque/emplacements/liste.html', context)


@login_required
def emplacement_detail_view(request, pk):
    """Détail d'un emplacement"""
    emplacement = get_object_or_404(
        EmplacementLivre.objects.select_related(
            'compartiment__etagere'
        ),
        pk=pk
    )
    
    context = {'emplacement': emplacement}
    return render(request, 'bibliotheque/emplacements/detail.html', context)


@login_required
def emplacement_create_view(request):
    """Création d'un emplacement"""
    compartiment_id = request.GET.get('compartiment')
    
    if request.method == 'POST':
        form = EmplacementLivreForm(request.POST)
        if form.is_valid():
            emplacement = form.save()
            messages.success(request, f"L'emplacement {emplacement.code_emplacement} a été créé avec succès.")
            return redirect('emplacement_detail', pk=emplacement.pk)
    else:
        initial = {}
        if compartiment_id:
            initial['compartiment'] = compartiment_id
        form = EmplacementLivreForm(initial=initial)
    
    context = {'form': form, 'action': 'Créer'}
    return render(request, 'bibliotheque/emplacements/form.html', context)


@login_required
def emplacement_update_view(request, pk):
    """Modification d'un emplacement"""
    emplacement = get_object_or_404(EmplacementLivre, pk=pk)
    
    if request.method == 'POST':
        form = EmplacementLivreForm(request.POST, instance=emplacement)
        if form.is_valid():
            form.save()
            messages.success(request, f"L'emplacement {emplacement.code_emplacement} a été modifié avec succès.")
            return redirect('emplacement_detail', pk=emplacement.pk)
    else:
        form = EmplacementLivreForm(instance=emplacement)
    
    context = {'form': form, 'emplacement': emplacement, 'action': 'Modifier'}
    return render(request, 'bibliotheque/emplacements/form.html', context)


@login_required
def emplacement_delete_view(request, pk):
    """Suppression d'un emplacement"""
    emplacement = get_object_or_404(EmplacementLivre, pk=pk)
    
    if request.method == 'POST':
        compartiment = emplacement.compartiment
        code = emplacement.code_emplacement
        emplacement.delete()
        messages.success(request, f"L'emplacement {code} a été supprimé avec succès.")
        return redirect('bibliotheque:compartiment_detail', pk=compartiment.pk)
    
    context = {'emplacement': emplacement}
    return render(request, 'bibliotheque/emplacements/delete.html', context)


# Décorateur pour vérifier si l'utilisateur est admin
def admin_required(view_func):
    decorated_view = user_passes_test(
        lambda u: u.is_staff or u.is_superuser,
        login_url='/admin/login/'
    )(view_func)
    return decorated_view


# ========== TABLEAU DE BORD PARAMÉTRAGE ==========

@login_required
@admin_required
def parametrage_dashboard_view(request):
    """Tableau de bord des paramètres"""
    params = ParametreBibliotheque.get_params()
    categories = CategorieEmprunteur.objects.filter(actif=True).count()
    jours_feries = JourFerie.objects.count()
    messages_actifs = MessageSysteme.objects.filter(actif=True).count()
    regles_actives = RegleMetier.objects.filter(actif=True).count()
    
    context = {
        'params': params,
        'stats': {
            'categories': categories,
            'jours_feries': jours_feries,
            'messages_actifs': messages_actifs,
            'regles_actives': regles_actives,
        }
    }
    return render(request, 'bibliotheque/parametrage/dashboard.html', context)


# ========== PARAMÈTRES GÉNÉRAUX ==========

@login_required
@admin_required
def parametres_generaux_view(request):
    """Afficher et modifier les paramètres généraux"""
    params = ParametreBibliotheque.get_params()
    
    if request.method == 'POST':
        form = ParametreBibliothequeForm(request.POST, request.FILES, instance=params)
        if form.is_valid():
            form.save()
            messages.success(request, "Les paramètres ont été mis à jour avec succès.")
            return redirect('parametres_generaux')
    else:
        form = ParametreBibliothequeForm(instance=params)
    
    context = {'form': form, 'params': params}
    return render(request, 'bibliotheque/parametrage/parametres_generaux.html', context)


# ========== CATÉGORIES D'EMPRUNTEURS ==========

@login_required
@admin_required
def categorie_emprunteur_list_view(request):
    """Liste des catégories d'emprunteurs"""
    search_query = request.GET.get('search', '')
    actif_filter = request.GET.get('actif', '')
    
    categories = CategorieEmprunteur.objects.all()
    
    if search_query:
        categories = categories.filter(
            Q(nom__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if actif_filter == 'oui':
        categories = categories.filter(actif=True)
    elif actif_filter == 'non':
        categories = categories.filter(actif=False)
    
    categories = categories.order_by('nom')
    
    context = {
        'categories': categories,
        'search_query': search_query,
        'actif_filter': actif_filter,
    }
    return render(request, 'bibliotheque/parametrage/categorie_list.html', context)


@login_required
@admin_required
def categorie_emprunteur_create_view(request):
    """Créer une catégorie d'emprunteur"""
    if request.method == 'POST':
        form = CategorieEmprunteurForm(request.POST)
        if form.is_valid():
            categorie = form.save()
            messages.success(request, f"La catégorie '{categorie.nom}' a été créée avec succès.")
            return redirect('categorie_emprunteur_list')
    else:
        form = CategorieEmprunteurForm()
    
    context = {'form': form, 'action': 'Créer'}
    return render(request, 'bibliotheque/parametrage/categorie_form.html', context)


@login_required
@admin_required
def categorie_emprunteur_update_view(request, pk):
    """Modifier une catégorie d'emprunteur"""
    categorie = get_object_or_404(CategorieEmprunteur, pk=pk)
    
    if request.method == 'POST':
        form = CategorieEmprunteurForm(request.POST, instance=categorie)
        if form.is_valid():
            form.save()
            messages.success(request, f"La catégorie '{categorie.nom}' a été modifiée avec succès.")
            return redirect('categorie_emprunteur_list')
    else:
        form = CategorieEmprunteurForm(instance=categorie)
    
    context = {'form': form, 'categorie': categorie, 'action': 'Modifier'}
    return render(request, 'bibliotheque/parametrage/categorie_form.html', context)


@login_required
@admin_required
def categorie_emprunteur_delete_view(request, pk):
    """Supprimer une catégorie d'emprunteur"""
    categorie = get_object_or_404(CategorieEmprunteur, pk=pk)

    if request.method == 'POST':
        nom = categorie.nom
        categorie.delete()
        messages.success(request, f"La catégorie '{nom}' a été supprimée avec succès.")
        return redirect('categorie_emprunteur_list')
    
    context = {'categorie': categorie}
    return render(request, 'bibliotheque/parametrage/categorie_delete.html', context)


# ========== JOURS FÉRIÉS ==========

@login_required
@admin_required
def jour_ferie_list_view(request):
    """Liste des jours fériés"""
    jours = JourFerie.objects.all().order_by('date')
    
    context = {'jours': jours}
    return render(request, 'bibliotheque/parametrage/jour_ferie_list.html', context)


@login_required
@admin_required
def jour_ferie_create_view(request):
    """Créer un jour férié"""
    if request.method == 'POST':
        form = JourFerieForm(request.POST)
        if form.is_valid():
            jour = form.save()
            messages.success(request, f"Le jour férié '{jour.nom}' a été créé avec succès.")
            return redirect('jour_ferie_list')
    else:
        form = JourFerieForm()
    
    context = {'form': form, 'action': 'Créer'}
    return render(request, 'bibliotheque/parametrage/jour_ferie_form.html', context)


@login_required
@admin_required
def jour_ferie_update_view(request, pk):
    """Modifier un jour férié"""
    jour = get_object_or_404(JourFerie, pk=pk)
    
    if request.method == 'POST':
        form = JourFerieForm(request.POST, instance=jour)
        if form.is_valid():
            form.save()
            messages.success(request, f"Le jour férié '{jour.nom}' a été modifié avec succès.")
            return redirect('jour_ferie_list')
    else:
        form = JourFerieForm(instance=jour)
    
    context = {'form': form, 'jour': jour, 'action': 'Modifier'}
    return render(request, 'bibliotheque/parametrage/jour_ferie_form.html', context)


@login_required
@admin_required
def jour_ferie_delete_view(request, pk):
    """Supprimer un jour férié"""
    jour = get_object_or_404(JourFerie, pk=pk)
    
    if request.method == 'POST':
        nom = jour.nom
        jour.delete()
        messages.success(request, f"Le jour férié '{nom}' a été supprimé avec succès.")
        return redirect('bibliotheque:jour_ferie_list')
    
    context = {'jour': jour}
    return render(request, 'bibliotheque/parametrage/jour_ferie_delete.html', context)


# ========== MESSAGES SYSTÈME ==========

@login_required
@admin_required
def message_systeme_list_view(request):
    """Liste des messages système"""
    messages_list = MessageSysteme.objects.all().order_by('-prioritaire', '-date_debut')
    
    context = {'messages_list': messages_list}
    return render(request, 'bibliotheque/parametrage/message_list.html', context)


@login_required
@admin_required
def message_systeme_create_view(request):
    """Créer un message système"""
    if request.method == 'POST':
        form = MessageSystemeForm(request.POST)
        if form.is_valid():
            msg = form.save()
            messages.success(request, f"Le message '{msg.titre}' a été créé avec succès.")
            return redirect('bibliotheque:message_systeme_list')
    else:
        form = MessageSystemeForm()
    
    context = {'form': form, 'action': 'Créer'}
    return render(request, 'bibliotheque/parametrage/message_form.html', context)


@login_required
@admin_required
def message_systeme_update_view(request, pk):
    """Modifier un message système"""
    msg = get_object_or_404(MessageSysteme, pk=pk)
    
    if request.method == 'POST':
        form = MessageSystemeForm(request.POST, instance=msg)
        if form.is_valid():
            form.save()
            messages.success(request, f"Le message '{msg.titre}' a été modifié avec succès.")
            return redirect('bibliotheque:message_systeme_list')
    else:
        form = MessageSystemeForm(instance=msg)
    
    context = {'form': form, 'message': msg, 'action': 'Modifier'}
    return render(request, 'bibliotheque/parametrage/message_form.html', context)


@login_required
@admin_required
def message_systeme_delete_view(request, pk):
    """Supprimer un message système"""
    msg = get_object_or_404(MessageSysteme, pk=pk)
    
    if request.method == 'POST':
        titre = msg.titre
        msg.delete()
        messages.success(request, f"Le message '{titre}' a été supprimé avec succès.")
        return redirect('message_systeme_list')
    
    context = {'message': msg}
    return render(request, 'bibliotheque/parametrage/message_delete.html', context)


# ========== CONFIGURATION EMAILS ==========

@login_required
@admin_required
def configuration_email_list_view(request):
    """Liste des configurations d'emails"""
    configs = ConfigurationEmail.objects.all().order_by('type_email')
    
    context = {'configs': configs}
    return render(request, 'bibliotheque/parametrage/email_list.html', context)


@login_required
@admin_required
def configuration_email_update_view(request, pk):
    """Modifier une configuration email"""
    config = get_object_or_404(ConfigurationEmail, pk=pk)
    
    if request.method == 'POST':
        form = ConfigurationEmailForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "La configuration email a été mise à jour avec succès.")
            return redirect('configuration_email_list')
    else:
        form = ConfigurationEmailForm(instance=config)
    
    context = {'form': form, 'config': config}
    return render(request, 'bibliotheque/parametrage/email_form.html', context)


# ============= VUES ABONNEMENTS =============

@login_required
def abonnement_list(request):
    """Liste des abonnements"""
    abonnements = Abonnement.objects.select_related('etudiant').order_by('-date_debut')
    
    # Filtres
    statut = request.GET.get('statut')
    if statut == 'actif':
        abonnements = abonnements.filter(actif=True)
    elif statut == 'inactif':
        abonnements = abonnements.filter(actif=False)
    
    paginator = Paginator(abonnements, 20)
    page = request.GET.get('page')
    abonnements = paginator.get_page(page)
    
    context = {'abonnements': abonnements}
    return render(request, 'bibliotheque/abonnements/abonnement_list.html', context)


@login_required
def abonnement_create(request):
    """Création d'un nouvel abonnement"""
    if request.method == 'POST':
        form = AbonnementForm(request.POST)
        if form.is_valid():
            abonnement = form.save()
            messages.success(request, 'Abonnement créé avec succès!')
            return redirect('abonnement_detail', pk=abonnement.pk)
        else:
            messages.error(request, 'Erreur lors de la création.')
    else:
        # Pré-remplir avec l'étudiant si fourni dans l'URL
        etudiant_id = request.GET.get('etudiant')
        initial = {'etudiant': etudiant_id} if etudiant_id else {}
        form = AbonnementForm(initial=initial)
    
    context = {'form': form, 'action': 'Créer'}
    return render(request, 'bibliotheque/abonnements/abonnement_form.html', context)


@login_required
def abonnement_update(request, pk):
    """Modification d'un abonnement"""
    abonnement = get_object_or_404(Abonnement, pk=pk)
    
    if request.method == 'POST':
        form = AbonnementForm(request.POST, instance=abonnement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Abonnement modifié avec succès!')
            return redirect('abonnement_detail', pk=abonnement.pk)
    else:
        form = AbonnementForm(instance=abonnement)
    
    context = {'form': form, 'action': 'Modifier', 'abonnement': abonnement}
    return render(request, 'bibliotheque/abonnements/abonnement_form.html', context)


@login_required
def abonnement_detail(request, pk):
    """Détails d'un abonnement"""
    abonnement = get_object_or_404(Abonnement, pk=pk)
    context = {'abonnement': abonnement}
    return render(request, 'bibliotheque/abonnements/abonnement_detail.html', context)


@login_required
def abonnement_delete(request, pk):
    """Suppression d'un abonnement"""
    abonnement = get_object_or_404(Abonnement, pk=pk)
    
    if request.method == 'POST':
        abonnement.delete()
        messages.success(request, 'Abonnement supprimé avec succès!')
        return redirect('abonnement_list')
    
    context = {'abonnement': abonnement}
    return render(request, 'bibliotheque/abonnements/abonnement_confirm_delete.html', context)


# ============= VUES UNIVERSITÉS =============

@login_required
def universite_list(request):
    """Liste des universités"""
    universites = Universite.objects.all().order_by('nom')
    
    context = {'universites': universites}
    return render(request, 'bibliotheque/universites/universite_list.html', context)


@login_required
def universite_create(request):
    """Création d'une nouvelle université"""
    if request.method == 'POST':
        form = UniversiteForm(request.POST)
        if form.is_valid():
            universite = form.save()
            messages.success(request, f'Université {universite.nom} créée avec succès!')
            return redirect('universite_detail', pk=universite.pk)
    else:
        form = UniversiteForm()
    
    context = {'form': form, 'action': 'Créer'}
    return render(request, 'bibliotheque/universites/universite_form.html', context)


@login_required
def universite_update(request, pk):
    """Modification d'une université"""
    universite = get_object_or_404(Universite, pk=pk)
    
    if request.method == 'POST':
        form = UniversiteForm(request.POST, instance=universite)
        if form.is_valid():
            form.save()
            messages.success(request, f'Université {universite.nom} modifiée avec succès!')
            return redirect('universite_detail', pk=universite.pk)
    else:
        form = UniversiteForm(instance=universite)
    
    context = {'form': form, 'action': 'Modifier', 'universite': universite}
    return render(request, 'bibliotheque/universites/universite_form.html', context)


@login_required
def universite_detail(request, pk):
    """Détails d'une université"""
    universite = get_object_or_404(Universite, pk=pk)
    etudiants = universite.etudiants.all()[:10]
    
    context = {
        'universite': universite,
        'etudiants': etudiants,
        'nb_etudiants': universite.etudiants.count()
    }
    return render(request, 'bibliotheque/universites/universite_detail.html', context)


@login_required
def universite_delete(request, pk):
    """Suppression d'une université"""
    universite = get_object_or_404(Universite, pk=pk)
    
    if request.method == 'POST':
        nom = universite.nom
        universite.delete()
        messages.success(request, f'Université {nom} supprimée avec succès!')
        return redirect('universite_list')
    
    context = {'universite': universite}
    return render(request, 'bibliotheque/universites/universite_confirm_delete.html', context)


# ============= VUES AUTEURS =============

@login_required
def auteur_list(request):
    """Liste des auteurs"""
    auteurs = Auteur.objects.all().order_by('nom', 'prenom')
    
    query = request.GET.get('q', '')
    if query:
        auteurs = auteurs.filter(
            Q(nom__icontains=query) | Q(prenom__icontains=query)
        )
    
    paginator = Paginator(auteurs, 20)
    page = request.GET.get('page')
    auteurs = paginator.get_page(page)
    
    context = {'auteurs': auteurs, 'query': query}
    return render(request, 'bibliotheque/auteurs/auteur_list.html', context)


@login_required
def auteur_create(request):
    """Création d'un nouvel auteur"""
    if request.method == 'POST':
        form = AuteurForm(request.POST)
        if form.is_valid():
            auteur = form.save()
            messages.success(request, f'Auteur {auteur.nom} créé avec succès!')
            return redirect('auteur_detail', pk=auteur.pk)
    else:
        form = AuteurForm()
    
    context = {'form': form, 'action': 'Créer'}
    return render(request, 'bibliotheque/auteurs/auteur_form.html', context)


@login_required
def auteur_update(request, pk):
    """Modification d'un auteur"""
    auteur = get_object_or_404(Auteur, pk=pk)
    
    if request.method == 'POST':
        form = AuteurForm(request.POST, instance=auteur)
        if form.is_valid():
            form.save()
            messages.success(request, f'{auteur.nom} modifié avec succès!')
            return redirect('auteur_detail', pk=auteur.pk)
    else:
        form = AuteurForm(instance=auteur)
    
    context = {'form': form, 'action': 'Modifier', 'auteur': auteur}
    return render(request, 'bibliotheque/auteurs/auteur_form.html', context)


@login_required
def auteur_detail(request, pk):
    """Détails d'un auteur"""
    auteur = get_object_or_404(Auteur, pk=pk)
    
    context = {'auteur': auteur}
    return render(request, 'bibliotheque/auteurs/auteur_detail.html', context)


@login_required
def auteur_delete(request, pk):
    """Suppression d'un auteur"""
    auteur = get_object_or_404(Auteur, pk=pk)
    
    if request.method == 'POST':
        nom = auteur.get_full_name()
        auteur.delete()
        messages.success(request, f'Auteur {nom} supprimé avec succès!')
        return redirect('auteur_list')
    
    context = {'auteur': auteur}
    return render(request, 'bibliotheque/auteurs/auteur_confirm_delete.html', context)


def users_list(request):
    """
    GET /api/users/
    """
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    users = User.objects.all().order_by("id")

    data = []
    for user in users:
        data.append({
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "is_active": user.is_active,
            "date_joined": user.date_joined,
            "last_login": user.last_login,
        })

    return JsonResponse({"users": data}, safe=False)


@csrf_exempt
def user_update(request, user_id):
    """
    PUT /api/users/<id>/
    """
    if request.method != "PUT":
        return HttpResponseNotAllowed(["PUT"])

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "Utilisateur introuvable"}, status=404)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON invalide"}, status=400)

    # Mise à jour des permissions
    user.is_staff = body.get("is_staff", user.is_staff)
    user.is_superuser = body.get("is_superuser", user.is_superuser)
    user.is_active = body.get("is_active", user.is_active)
    user.save()

    return JsonResponse({
        "message": "Permissions mises à jour avec succès",
        "user_id": user.id
    })


# ========== RÉCUPÉRER TOUS LES UTILISATEURS ==========

@login_required
@require_http_methods(["GET"])
def get_users(request):
    """
    Récupère tous les utilisateurs de la table auth_user
    Retourne directement les données sans JSON intermédiaire
    URL: /users/ ou /api/users/
    """
    from django.shortcuts import render
    
    try:
        # Récupérer tous les utilisateurs directement depuis la base de données
        users = User.objects.all().order_by('id')
        
        # Calculer les statistiques
        total_users = users.count()
        total_staff = users.filter(is_staff=True).count()
        total_superusers = users.filter(is_superuser=True).count()
        total_active = users.filter(is_active=True).count()
        
        # Préparer le contexte pour le template
        context = {
            'users': users,
            'total_users': total_users,
            'total_staff': total_staff,
            'total_superusers': total_superusers,
            'total_active': total_active,
        }
        
        # Retourner le template HTML avec les données
        return render(request, 'bibliotheque/parametrage/users_management.html', context)
        
    except Exception as e:
        context = {
            'error': str(e),
            'users': []
        }
        return render(request, 'bibliotheque/parametrage/users_management.html', context)




# ========== RÉCUPÉRER UN UTILISATEUR PAR ID ==========
@require_http_methods(["GET"])
@login_required
def get_user_by_id(request, user_id):
    """
    Récupère un utilisateur spécifique par son ID
    URL: /api/users/<id>/
    """
    try:
        user = User.objects.get(id=user_id)
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'is_active': user.is_active,
            'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
            'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None
        }
        
        return JsonResponse({
            'success': True,
            'user': user_data
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'Utilisateur avec ID {user_id} introuvable'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ========== METTRE À JOUR LES DROITS D'UN UTILISATEUR ==========
@csrf_exempt
@login_required
@require_http_methods(["PUT", "PATCH"])
def update_user_permissions(request, user_id):
    """
    Met à jour les droits d'accès d'un utilisateur
    URL: /api/users/<id>/
    Body: {
        "is_staff": true/false,
        "is_superuser": true/false,
        "is_active": true/false
    }
    """
    try:
        data = json.loads(request.body)
        user = User.objects.get(id=user_id)
        
        # Mettre à jour les permissions
        if 'is_staff' in data:
            user.is_staff = data['is_staff']
        
        if 'is_superuser' in data:
            user.is_superuser = data['is_superuser']
        
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        # Sauvegarder les modifications
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Droits de {user.username} mis à jour avec succès',
            'user': {
                'id': user.id,
                'username': user.username,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'is_active': user.is_active
            }
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'Utilisateur avec ID {user_id} introuvable'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Données JSON invalides'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ========== METTRE À JOUR TOUTES LES INFOS D'UN UTILISATEUR ==========
@csrf_exempt
@login_required
@require_http_methods(["PUT"])
def update_user_complete(request, user_id):
    """
    Met à jour toutes les informations d'un utilisateur
    URL: /api/users/<id>/complete/
    """
    try:
        data = json.loads(request.body)
        user = User.objects.get(id=user_id)
        
        # Mettre à jour tous les champs disponibles
        if 'username' in data:
            user.username = data['username']
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            user.email = data['email']
        if 'is_staff' in data:
            user.is_staff = data['is_staff']
        if 'is_superuser' in data:
            user.is_superuser = data['is_superuser']
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Utilisateur {user.username} mis à jour avec succès',
            'user': {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'is_active': user.is_active
            }
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'Utilisateur avec ID {user_id} introuvable'
        }, status=404)
    except IntegrityError as e:
        return JsonResponse({
            'success': False,
            'error': 'Ce nom d\'utilisateur ou email existe déjà'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ========== SUPPRIMER UN UTILISATEUR ==========
@csrf_exempt
@login_required
@require_http_methods(["DELETE"])
def delete_user(request, user_id):
    """
    Supprime un utilisateur
    URL: /api/users/<id>/
    """
    try:
        user = User.objects.get(id=user_id)
        username = user.username
        user.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Utilisateur {username} supprimé avec succès'
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'Utilisateur avec ID {user_id} introuvable'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ========== RECHERCHER DES UTILISATEURS ==========
@require_http_methods(["GET"])
@login_required
def search_users(request):
    """
    Recherche des utilisateurs par nom, email ou username
    URL: /api/users/search/?q=<terme_recherche>
    """
    try:
        query = request.GET.get('q', '')
        
        if not query:
            return JsonResponse({
                'success': False,
                'error': 'Paramètre de recherche "q" manquant'
            }, status=400)
        
        # Recherche dans plusieurs champs
        users = User.objects.filter(
            username__icontains=query
        ) | User.objects.filter(
            first_name__icontains=query
        ) | User.objects.filter(
            last_name__icontains=query
        ) | User.objects.filter(
            email__icontains=query
        )
        
        users_list = list(users.values(
            'id', 'username', 'first_name', 'last_name',
            'email', 'is_staff', 'is_superuser', 'is_active',
            'date_joined', 'last_login'
        ))
        
        # Formater les dates
        for user in users_list:
            if user['date_joined']:
                user['date_joined'] = user['date_joined'].strftime('%Y-%m-%d %H:%M:%S')
            if user['last_login']:
                user['last_login'] = user['last_login'].strftime('%Y-%m-%d %H:%M:%S')
        
        return JsonResponse({
            'success': True,
            'count': len(users_list),
            'results': users_list
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ========== STATISTIQUES DES UTILISATEURS ==========
@require_http_methods(["GET"])
@login_required
def get_users_stats(request):
    """
    Retourne les statistiques des utilisateurs
    URL: /api/users/stats/
    """
    try:
        total_users = User.objects.count()
        total_staff = User.objects.filter(is_staff=True).count()
        total_superusers = User.objects.filter(is_superuser=True).count()
        total_active = User.objects.filter(is_active=True).count()
        total_inactive = User.objects.filter(is_active=False).count()
        
        return JsonResponse({
            'success': True,
            'stats': {
                'total_users': total_users,
                'total_staff': total_staff,
                'total_superusers': total_superusers,
                'total_active': total_active,
                'total_inactive': total_inactive
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# ========== AFFICHER LA PAGE D'AJOUT ==========
@require_http_methods(["GET"])
@login_required
def add_user_page(request):
    """
    Affiche la page pour ajouter un nouvel utilisateur
    URL: /users/add/
    """
    return render(request, 'bibliotheque/parametrage/add_user.html')


# ========== CRÉER UN NOUVEL UTILISATEUR ==========
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_user_form(request):
    """
    Crée un nouvel utilisateur depuis le formulaire HTML
    URL: /users/create/
    
    Récupère les données depuis request.POST:
    - username
    - first_name
    - last_name
    - email
    - password
    - is_active (checkbox)
    - is_staff (checkbox)
    - is_superuser (checkbox)
    """
    try:
        # Récupérer les données du formulaire
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        # Les checkboxes envoient 'on' si cochées, None sinon
        is_active = request.POST.get('is_active') == 'on'
        is_staff = request.POST.get('is_staff') == 'on'
        is_superuser = request.POST.get('is_superuser') == 'on'
        
        # Validation des champs obligatoires
        if not username or len(username) < 3:
            return render(request, 'add_user.html', {
                'error': 'Le nom d\'utilisateur doit contenir au moins 3 caractères'
            })
        
        if not email or '@' not in email:
            return render(request, 'add_user.html', {
                'error': 'Veuillez entrer une adresse email valide'
            })
        
        if not password or len(password) < 8:
            return render(request, 'bibliotheque/parametrage/add_user.html', {
                'error': 'Le mot de passe doit contenir au moins 8 caractères'
            })
        
        # Vérifier si le username existe déjà
        if User.objects.filter(username=username).exists():
            return render(request, 'bibliotheque/parametrage/add_user.html', {
                'error': f'Le nom d\'utilisateur "{username}" existe déjà'
            })
        
        # Vérifier si l'email existe déjà
        if User.objects.filter(email=email).exists():
            return render(request, 'bibliotheque/parametrage/add_user.html', {
                'error': f'L\'adresse email "{email}" est déjà utilisée'
            })
        
        # Créer l'utilisateur dans la table auth_user
        user = User.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=make_password(password),  # Hasher le mot de passe
            is_active=is_active,
            is_staff=is_staff,
            is_superuser=is_superuser
        )
        
        # Rediriger vers la page de détails du nouvel utilisateur
        # return redirect('user_detail', user_id=user.id)
        
    except Exception as e:
        return render(request, 'bibliotheque/parametrage/add_user.html', {
            'error': f'Erreur lors de la création: {str(e)}'
        })


# ========== EXEMPLE: Créer un utilisateur programmatiquement ==========
@login_required
def create_user_example():
    """
    Exemple de fonction pour créer un utilisateur directement
    Utilisable dans le shell Django ou dans vos vues
    """
    user = User.objects.create(
        username='test_user',
        first_name='Test',
        last_name='Utilisateur',
        email='test@example.com',
        password=make_password('password123'),
        is_active=True,
        is_staff=False,
        is_superuser=False
    )
    
    print(f"Utilisateur créé: {user.username} (ID: {user.id})")
    return user





class RechercheEtudiantView(ListView):
    """Vue pour rechercher un étudiant avant l'emprunt"""
    model = Etudiant1
    template_name = 'bibliotheque/recherche_etudiant.html'
    context_object_name = 'etudiants'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Etudiant1.objects.filter(statut='actif')
        recherche = self.request.GET.get('q', '')
        
        if recherche:
            # Recherche dans la base locale
            queryset = queryset.filter(
                Q(matricule__icontains=recherche) |
                Q(nom__icontains=recherche) |
                Q(prenom__icontains=recherche) |
                Q(email__icontains=recherche)
            ).select_related('universite', 'faculte', 'departement', 'classe')
            
            # Si aucun résultat local, chercher dans l'API
            if not queryset.exists() and len(recherche) >= 3:
                try:
                    etudiant_api = Etudiant1.rechercher_pour_emprunt(recherche)
                    if etudiant_api:
                        messages.success(
                            self.request,
                            f"Étudiant '{etudiant_api.nom_complet}' récupéré depuis l'API et ajouté à la base."
                        )
                        queryset = Etudiant1.objects.filter(pk=etudiant_api.pk)
                    else:
                        messages.warning(
                            self.request,
                            "Aucun étudiant trouvé dans la base locale ni dans l'API externe."
                        )
                except Exception as e:
                    messages.error(
                        self.request,
                        f"Erreur lors de la recherche dans l'API: {str(e)}"
                    )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recherche'] = self.request.GET.get('q', '')
        context['form'] = RechercheEtudiantForm(self.request.GET or None)
        return context

@login_required
def creer_emprunt_etudiant(request, etudiant_pk):
    """Vue pour créer un emprunt pour un étudiant spécifique"""
    etudiant = get_object_or_404(Etudiant1, pk=etudiant_pk)
    
    # Vérifier si l'étudiant peut emprunter
    if not etudiant.peut_emprunter():
        messages.error(
            request,
            f"L'étudiant {etudiant.nom_complet} ne peut pas emprunter (statut: {etudiant.get_statut_display()})"
        )
        return redirect('recherche_etudiant')
    
    if request.method == 'POST':
        form = EmpruntForm(request.POST)
        if form.is_valid():
            emprunt = form.save(commit=False)
            emprunt.etudiant = etudiant
            
            # Vérifier la disponibilité du livre
            livre = emprunt.livre
            if livre.nombre_exemplaires_disponibles <= 0:
                messages.error(request, f"Le livre '{livre.titre}' n'est pas disponible.")
                return render(request, 'bibliotheque/etudiants/creer_emprunt.html', {
                    'form': form,
                    'etudiant': etudiant
                })
            
            # Sauvegarder l'emprunt
            emprunt.save()
            
            # Mettre à jour le stock du livre
            livre.nombre_exemplaires_disponibles -= 1
            livre.save()
            
            messages.success(
                request,
                f"Emprunt créé avec succès pour {etudiant.nom_complet}"
            )
            return redirect('emprunt_detail', pk=emprunt.pk)
    else:
        form = EmpruntForm()
    
    return render(request, 'bibliotheque/etudiants/creer_emprunt.html', {
        'form': form,
        'etudiant': etudiant
    })

@login_required
def recherche_rapide_etudiant_api(request):
    """Vue AJAX pour recherche rapide avec l'API"""
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        recherche = request.GET.get('q', '')
        resultats = []
        
        if len(recherche) >= 3:
            # Recherche dans la base locale
            etudiants_locaux = Etudiant1.objects.filter(
                Q(matricule__icontains=recherche) |
                Q(nom__icontains=recherche) |
                Q(prenom__icontains=recherche) |
                Q(email__icontains=recherche),
                statut='actif'
            )[:10]
            
            for etudiant in etudiants_locaux:
                resultats.append({
                    'id': etudiant.pk,
                    'matricule': etudiant.matricule,
                    'nom_complet': etudiant.nom_complet,
                    'email': etudiant.email,
                    'parcours': etudiant.parcours_academique,
                    'source': 'local'
                })
            
            # Si moins de 10 résultats, chercher dans l'API
            if len(resultats) < 10:
                try:
                    etudiant_api = Etudiant1.rechercher_pour_emprunt(recherche)
                    if etudiant_api and etudiant_api.pk not in [r['id'] for r in resultats]:
                        resultats.append({
                            'id': etudiant_api.pk,
                            'matricule': etudiant_api.matricule,
                            'nom_complet': etudiant_api.nom_complet,
                            'email': etudiant_api.email,
                            'parcours': etudiant_api.parcours_academique,
                            'source': 'api'
                        })
                except Exception:
                    pass  # Ignorer les erreurs API en recherche rapide
        
        return JsonResponse({'resultats': resultats})
    
    return JsonResponse({'error': 'Requête invalide'}, status=400)

@login_required
class SyncEtudiantsAPIView(ListView):
    """Vue pour synchroniser manuellement des étudiants depuis l'API"""
    template_name = 'bibliotheque/etudiants/sync_etudiants_api.html'
    
    def post(self, request, *args, **kwargs):
        matricules = request.POST.get('matricules', '').split('\n')
        succes = 0
        erreurs = []
        
        for matricule in matricules:
            matricule = matricule.strip()
            if not matricule:
                continue
            
            try:
                etudiant = Etudiant1.recuperer_depuis_api(matricule=matricule)
                if etudiant:
                    succes += 1
                else:
                    erreurs.append(f"{matricule}: Non trouvé dans l'API")
            except Exception as e:
                erreurs.append(f"{matricule}: {str(e)}")
        
        if succes > 0:
            messages.success(request, f"{succes} étudiant(s) synchronisé(s) avec succès.")
        
        if erreurs:
            messages.warning(
                request,
                f"Erreurs lors de la synchronisation:\n" + "\n".join(erreurs[:5])
            )
        
        return redirect('etudiants/sync-api/')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['etudiants_syncs'] = Etudiant.objects.filter(
            sync_depuis_api=True
        ).order_by('-derniere_sync')[:50]
        return context
    
    @login_required 
    class Etudiant1DetailView(DetailView):
        """Vue pour afficher les détails d'un étudiant"""
    model = Etudiant
    template_name = 'bibliotheque/etudiants/etudiant1_detail.html'
    context_object_name = 'etudiant'
    
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     etudiant = Etudiant.objects.all()
        
    #     # Récupérer les emprunts de l'étudiant
    #     context['emprunts_en_cours'] = Emprunt.objects.filter(
    #         etudiant=etudiant,
    #         date_retour_effective__isnull=True
    #     ).select_related('livre')
        
    #     context['emprunts_historique'] = Emprunt.objects.filter(
    #         etudiant=etudiant,
    #        date_retour_effective__isnull=False
    #     ).select_related('livre').order_by('-date_retour_effective')[:10]
        
    #     # Statistiques
    #     context['total_emprunts'] = Emprunt.objects.filter(etudiant=etudiant).count()
    #     context['emprunts_actifs'] = context['emprunts_en_cours'].count()
        
    #     return context
    
    @login_required 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        etudiant = get_object_or_404(Etudiant, pk=self.kwargs.get('pk'))  # un seul objet

        context['emprunts_en_cours'] = Emprunt.objects.filter(
        etudiant=etudiant,
        date_retour_effective__isnull=True
        ).select_related('livre')

        context['emprunts_historique'] = Emprunt.objects.filter(
        etudiant=etudiant,
        date_retour_effective__isnull=False
       ).select_related('livre')

        return context
    
    
    
    
    
@login_required
def sync_etudiants_api(request):
    """Vue pour synchroniser manuellement des étudiants depuis l'API"""
    
    if request.method == 'POST':
        matricules = request.POST.get('matricules', '').split('\n')
        succes = 0
        erreurs = []
        
        for matricule in matricules:
            matricule = matricule.strip()
            if not matricule:
                continue
            
            try:
                etudiant = Etudiant1.recuperer_depuis_api(matricule=matricule)
                if etudiant:
                    succes += 1
                else:
                    erreurs.append(f"{matricule}: Non trouvé dans l'API")
            except Exception as e:
                erreurs.append(f"{matricule}: {str(e)}")
        
        if succes > 0:
            messages.success(request, f"{succes} étudiant(s) synchronisé(s) avec succès.")
        
        if erreurs:
            messages.warning(
                request,
                f"Erreurs lors de la synchronisation:\n" + "\n".join(erreurs[:5])
            )
        
        return redirect('bibliothech:sync_etudiants_api')
    
    # GET request
    etudiants_syncs = Etudiant1.objects.filter(
        sync_depuis_api=True
    ).order_by('-derniere_sync')[:50]
    
    context = {
        'etudiants_syncs': etudiants_syncs
    }
    
    return render(request, 'bibliotheque/etudiants/sync_etudiants_api.html', context)


# Vue pour afficher les détails d'un étudiant
@login_required
def etudiant_detail(request, pk):
    """Vue pour afficher les détails d'un étudiant"""
    
    etudiant = get_object_or_404(Etudiant, pk=pk)
    
    # Récupérer les emprunts de l'étudiant
    emprunts_en_cours = Emprunt.objects.filter(
        etudiant=etudiant,
        date_retour_effective__isnull=True
    ).select_related('livre')
    
    emprunts_historique = Emprunt.objects.filter(
        etudiant=etudiant,
        date_retour_effective__isnull=False
    ).select_related('livre').order_by('-date_retour_effective')[:10]
    
    # Statistiques
    total_emprunts = Emprunt.objects.filter(etudiant=etudiant).count()
    emprunts_actifs = emprunts_en_cours.count()
    
    context = {
        'etudiant': etudiant,
        'emprunts_en_cours': emprunts_en_cours,
        'emprunts_historique': emprunts_historique,
        'total_emprunts': total_emprunts,
        'emprunts_actifs': emprunts_actifs,
    }
    
    return render(request, 'bibliotheque/etudiants/etudiant1_detail.html', context)


# Vue pour lister tous les étudiants
@login_required
def liste_etudiants(request):
    """Vue pour afficher la liste de tous les étudiants"""
    
    # Filtres optionnels
    search = request.GET.get('search', '')
    
    etudiants = Etudiant1.objects.all()
    
    if search:
        etudiants = etudiants.filter(
            nom__icontains=search
        ) | etudiants.filter(
            prenom__icontains=search
        ) | etudiants.filter(
            matricule__icontains=search
        )
    
    etudiants = etudiants.order_by('nom', 'prenom')
    
    context = {
        'etudiants': etudiants,
        'search': search,
    }
    
    return render(request, 'bibliotheque/etudiants/sync_etudiants_api.html', context)


# Vue pour ajouter un étudiant
@login_required
def ajouter_etudiant(request):
    """Vue pour ajouter un nouvel étudiant"""
    
    if request.method == 'POST':
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        matricule = request.POST.get('matricule')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone', '')
        
        # Validation
        if not all([nom, prenom, matricule, email]):
            messages.error(request, 'Tous les champs obligatoires doivent être remplis.')
            return render(request, 'bibliotheque/etudiants/ajouter_etudiant.html')
        
        # Vérifier si le matricule existe déjà
        if Etudiant1.objects.filter(matricule=matricule).exists():
            messages.error(request, f'Un étudiant avec le matricule {matricule} existe déjà.')
            return render(request, 'bibliotheque/etudiants/ajouter_etudiant.html')
        
        try:
            etudiant = Etudiant.objects.create(
                nom=nom,
                prenom=prenom,
                matricule=matricule,
                email=email,
                telephone=telephone
            )
            messages.success(request, f'Étudiant {etudiant.nom} {etudiant.prenom} ajouté avec succès.')
            return redirect('bibliothech:etudiant_detail', pk=etudiant.pk)
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'ajout: {str(e)}')
    
    return render(request, 'bibliotheque/etudiants/ajouter_etudiant.html')


# Vue pour modifier un étudiant
@login_required
def modifier_etudiant(request, pk):
    """Vue pour modifier un étudiant existant"""
    
    etudiant = get_object_or_404(Etudiant, pk=pk)
    
    if request.method == 'POST':
        etudiant.nom = request.POST.get('nom')
        etudiant.prenom = request.POST.get('prenom')
        etudiant.email = request.POST.get('email')
        etudiant.telephone = request.POST.get('telephone', '')
        
        # Validation
        if not all([etudiant.nom, etudiant.prenom, etudiant.email]):
            messages.error(request, 'Tous les champs obligatoires doivent être remplis.')
        else:
            try:
                etudiant.save()
                messages.success(request, f'Étudiant {etudiant.nom} {etudiant.prenom} modifié avec succès.')
                return redirect('bibliothech:etudiant_detail', pk=etudiant.pk)
            except Exception as e:
                messages.error(request, f'Erreur lors de la modification: {str(e)}')
    
    context = {
        'etudiant': etudiant
    }
    
    return render(request, 'bibliotheque/etudiants/modifier_etudiant.html', context)


# Vue pour supprimer un étudiant
@login_required
def supprimer_etudiant(request, pk):
    """Vue pour supprimer un étudiant"""
    
    etudiant = get_object_or_404(Etudiant1, pk=pk)
    
    if request.method == 'POST':
        # Vérifier si l'étudiant a des emprunts en cours
        emprunts_en_cours = Emprunt.objects.filter(
            etudiant=etudiant,
            date_retour_effective__isnull=True
        ).count()
        
        if emprunts_en_cours > 0:
            messages.error(
                request, 
                f'Impossible de supprimer {etudiant.nom} {etudiant.prenom}. '
                f'Il/Elle a {emprunts_en_cours} emprunt(s) en cours.'
            )
            return redirect('bibliothech:etudiant_detail', pk=etudiant.pk)
        
        nom_complet = f"{etudiant.nom} {etudiant.prenom}"
        etudiant.delete()
        messages.success(request, f'Étudiant {nom_complet} supprimé avec succès.')
        return redirect('bibliothech:liste_etudiants')
    
    context = {
        'etudiant': etudiant
    }
    
    return render(request, 'bibliotheque/etudiants/supprimer_etudiant.html', context)


# Vue API JSON pour récupérer les étudiants
@login_required
def api_etudiants(request):
    """API pour récupérer la liste des étudiants au format JSON"""
    from django.http import JsonResponse
    
    etudiants = Etudiant1.objects.all().values(
        'id', 'nom', 'prenom', 'matricule', 'email', 'telephone'
    )
    
    return JsonResponse(list(etudiants), safe=False)


# Vue API pour récupérer un étudiant spécifique
@login_required
def api_etudiant_detail(request, pk):
    """API pour récupérer les détails d'un étudiant au format JSON"""
    from django.http import JsonResponse
    
    etudiant = get_object_or_404(Etudiant, pk=pk)
    
    data = {
        'id': etudiant.id,
        'nom': etudiant.nom,
        'prenom': etudiant.prenom,
        'matricule': etudiant.matricule,
        'email': etudiant.email,
        'telephone': etudiant.telephone,
        'emprunts_actifs': Emprunt.objects.filter(
            etudiant=etudiant,
            date_retour_effective__isnull=True
        ).count(),
        'total_emprunts': Emprunt.objects.filter(etudiant=etudiant).count(),
    }
    
    return JsonResponse(data)




def ajouter_etudiant(request):
    if request.method == 'POST':
        form = EtudiantForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_etudiants')
    else:
        form = EtudiantForm()
    
    return render(request, 'bibliotheque/etudiants/ajouter_etudiant.html', {'form': form})



# views.py - Ajouter ces fonctions

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Universite, Faculte1, Departement, Classe


# ===== Vues AJAX pour les selects en cascade =====

@login_required
def get_facultes(request):
    """
    Retourne les facultés d'une université en JSON
    URL: /api/get-facultes/?universite_id=1
    """
    universite_id = request.GET.get('universite_id')
    
    if not universite_id:
        return JsonResponse([], safe=False)
    
    try:
        facultes = Faculte1.objects.filter(
            universite_id=universite_id
        ).values('id', 'nom').order_by('nom')
        
        return JsonResponse(list(facultes), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def get_departements(request):
    """
    Retourne les départements d'une faculté en JSON
    URL: /api/get-departements/?faculte_id=1
    """
    faculte_id = request.GET.get('faculte_id')
    
    if not faculte_id:
        return JsonResponse([], safe=False)
    
    try:
        departements = Departement.objects.filter(
            faculte_id=faculte_id
        ).values('id', 'nom').order_by('nom')
        
        return JsonResponse(list(departements), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def get_classes(request):
    """
    Retourne les classes d'un département en JSON
    URL: /api/get-classes/?departement_id=1
    """
    departement_id = request.GET.get('departement_id')
    
    if not departement_id:
        return JsonResponse([], safe=False)
    
    try:
        classes = Classe.objects.filter(
            departement_id=departement_id
        ).values('id', 'nom').order_by('nom')
        
        return JsonResponse(list(classes), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def get_niveaux(request):
    """
    Retourne tous les niveaux d'étude disponibles
    URL: /api/get-niveaux/
    """
    # Si vous avez un modèle Niveau
    # niveaux = Niveau.objects.all().values('id', 'nom').order_by('ordre')
    
    # Sinon, liste prédéfinie
    niveaux = [
        {'id': 'L1', 'nom': 'Licence 1'},
        {'id': 'L2', 'nom': 'Licence 2'},
        {'id': 'L3', 'nom': 'Licence 3'},
        {'id': 'M1', 'nom': 'Master 1'},
        {'id': 'M2', 'nom': 'Master 2'},
        {'id': 'D1', 'nom': 'Doctorat 1'},
        {'id': 'D2', 'nom': 'Doctorat 2'},
        {'id': 'D3', 'nom': 'Doctorat 3'},
    ]
    
    return JsonResponse(niveaux, safe=False)


@login_required
def get_universites(request):
    """
    Retourne toutes les universités
    URL: /api/get-universites/
    """
    try:
        universites = Universite.objects.all().values(
            'id', 'nom', 'sigle', 'ville', 'pays'
        ).order_by('nom')
        
        return JsonResponse(list(universites), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ===== Fonction utilitaire pour récupérer toutes les données =====

def recuperer_donnees_academiques():
    """
    Fonction utilitaire pour récupérer toutes les données académiques
    Retourne un dictionnaire avec universités, facultés, départements, classes et niveaux
    """
    try:
        # Récupérer toutes les universités
        universites = list(Universite.objects.all().values(
            'id', 'nom', 'sigle', 'ville', 'pays'
        ).order_by('nom'))
        
        # Récupérer toutes les facultés avec leur université
        facultes = list(Faculte1.objects.select_related('universite').values(
            'id', 'nom', 'sigle', 'universite_id', 'universite__nom'
        ).order_by('nom'))
        
        # Récupérer tous les départements avec leur faculté
        departements = list(Departement.objects.select_related('faculte').values(
            'id', 'nom', 'sigle', 'faculte_id', 'faculte__nom'
        ).order_by('nom'))
        
        # Récupérer toutes les classes avec leur département
        classes = list(Classe.objects.select_related('departement').values(
            'id', 'nom', 'code', 'departement_id', 'departement__nom'
        ).order_by('nom'))
        
        # Niveaux d'étude (liste prédéfinie ou depuis la base de données)
        niveaux = [
            {'id': 'L1', 'nom': 'Licence 1'},
            {'id': 'L2', 'nom': 'Licence 2'},
            {'id': 'L3', 'nom': 'Licence 3'},
            {'id': 'M1', 'nom': 'Master 1'},
            {'id': 'M2', 'nom': 'Master 2'},
            {'id': 'D1', 'nom': 'Doctorat 1'},
            {'id': 'D2', 'nom': 'Doctorat 2'},
            {'id': 'D3', 'nom': 'Doctorat 3'},
        ]
        
        return {
            'success': True,
            'universites': universites,
            'facultes': facultes,
            'departements': departements,
            'classes': classes,
            'niveaux': niveaux,
            'total_universites': len(universites),
            'total_facultes': len(facultes),
            'total_departements': len(departements),
            'total_classes': len(classes),
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@login_required
def get_all_donnees_academiques(request):
    """
    Vue pour récupérer toutes les données académiques en une seule requête
    URL: /api/get-all-donnees/
    """
    donnees = recuperer_donnees_academiques()
    return JsonResponse(donnees, safe=False)


# ===== Fonction pour récupérer les facultés d'une université spécifique =====

def get_facultes_by_universite(universite_id):
    """
    Récupère les facultés d'une université spécifique
    Args:
        universite_id: ID de l'université
    Returns:
        QuerySet des facultés
    """
    try:
        return Faculte1.objects.filter(
            universite_id=universite_id
        ).select_related('universite').order_by('nom')
    except Exception as e:
        print(f"Erreur lors de la récupération des facultés: {e}")
        return Faculte1.objects.none()


def get_departements_by_faculte(faculte_id):
    """
    Récupère les départements d'une faculté spécifique
    Args:
        faculte_id: ID de la faculté
    Returns:
        QuerySet des départements
    """
    try:
        return Departement.objects.filter(
            faculte_id=faculte_id
        ).select_related('faculte').order_by('nom')
    except Exception as e:
        print(f"Erreur lors de la récupération des départements: {e}")
        return Departement.objects.none()


def get_classes_by_departement(departement_id):
    """
    Récupère les classes d'un département spécifique
    Args:
        departement_id: ID du département
    Returns:
        QuerySet des classes
    """
    try:
        return Classe.objects.filter(
            departement_id=departement_id
        ).select_related('departement').order_by('nom')
    except Exception as e:
        print(f"Erreur lors de la récupération des classes: {e}")
        return Classe.objects.none()


# ===== Fonction pour récupérer la hiérarchie complète =====

def get_hierarchie_academique(universite_id=None, faculte_id=None, departement_id=None):
    """
    Récupère la hiérarchie académique complète ou partielle
    Args:
        universite_id: ID de l'université (optionnel)
        faculte_id: ID de la faculté (optionnel)
        departement_id: ID du département (optionnel)
    Returns:
        Dictionnaire avec la hiérarchie
    """
    hierarchie = {}
    
    try:
        if universite_id:
            # Université spécifique
            hierarchie['universite'] = Universite.objects.get(id=universite_id)
            hierarchie['facultes'] = list(Faculte1.objects.filter(
                universite_id=universite_id
            ).values('id', 'nom', 'sigle'))
            
            if faculte_id:
                # Faculté spécifique
                hierarchie['faculte'] = Faculte1.objects.get(id=faculte_id)
                hierarchie['departements'] = list(Departement.objects.filter(
                    faculte_id=faculte_id
                ).values('id', 'nom', 'sigle'))
                
                if departement_id:
                    # Département spécifique
                    hierarchie['departement'] = Departement.objects.get(id=departement_id)
                    hierarchie['classes'] = list(Classe.objects.filter(
                        departement_id=departement_id
                    ).values('id', 'nom', 'code'))
        else:
            # Tout récupérer
            hierarchie = recuperer_donnees_academiques()
        
        hierarchie['success'] = True
        
    except Exception as e:
        hierarchie = {
            'success': False,
            'error': str(e)
        }
    
    return hierarchie



# views.py - Vues pour la gestion hiérarchique

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Universite, Faculte1, Departement, Classe, Etudiant
from .forms import UniversiteForm, Faculte1Form, DepartementForm, ClasseForm


# ==================== UNIVERSITÉ ====================

@login_required
def universite_detail(request, pk):
    """
    Vue détaillée d'une université avec sa structure hiérarchique
    """
    universite = get_object_or_404(Universite, pk=pk)
    
    # Récupérer les facultés avec leurs compteurs
    facultes = Faculte1.objects.filter(universite=universite).annotate(
        nb_departements=Count('departements')
    ).prefetch_related('departements__classes')
    
    # universite = Universite.objects.prefetch_related('faculte').get(pk=pk)
    
    # Préparer les données hiérarchiques
    facultes_data = []
    for faculte in facultes:
        departements = Departement.objects.filter(faculte=faculte).annotate(
            nb_classes=Count('classes')
        ).prefetch_related('classes')
        
        departements_data = []
        for departement in departements:
            classes = Classe.objects.filter(departement=departement).annotate(
                nb_etudiants=Count('etudiants1')
            )
            
            departements_data.append({
                'id': departement.id,
                'nom': departement.nom,
                'sigle': departement.sigle,
                'nb_classes': classes.count(),
                'classes_list': classes
            })
        
        facultes_data.append({
            'id': faculte.id,
            'nom': faculte.nom,
            'sigle': faculte.sigle,
            'nb_departements': departements.count(),
            'departements_list': departements_data
        })
    
    # Statistiques
    nb_facultes = facultes.count()
    nb_departements = Departement.objects.filter(faculte__universite=universite).count()
    nb_classes = Classe.objects.filter(departement__faculte__universite=universite).count()
    nb_etudiants = Etudiant1.objects.filter(universite=universite).count()
    
    # Étudiants (limité à 10)
    etudiants = Etudiant1.objects.filter(universite=universite).select_related(
        'faculte', 'departement', 'classe'
    )[:10]
    
    context = {
        'universite': universite,
        'facultes': facultes_data,
        'nb_facultes': nb_facultes,
        'nb_departements': nb_departements,
        'nb_classes': nb_classes,
        'nb_etudiants': nb_etudiants,
        'etudiants': etudiants,
    }
    
    return render(request, 'bibliotheque/universites/universite_detail.html', context)


# ==================== FACULTÉ ====================

@login_required
def faculte_create(request, universite_pk):
    """
    Créer une faculté pour une université
    """
    universite = get_object_or_404(Universite, pk=universite_pk)
    
    if request.method == 'POST':
        form = Faculte1Form(request.POST)
        if form.is_valid():
            faculte = form.save(commit=False)
            faculte.universite = universite
            faculte.save()
            messages.success(request, f'La faculté "{faculte.nom}" a été créée avec succès.')
            return redirect('universite_detail', pk=universite.pk)
    else:
        form = Faculte1Form()
    
    context = {
        'form': form,
        'universite': universite,
        'titre': 'Ajouter une faculté',
        'action': 'Créer'
    }
    return render(request, 'bibliotheque/etudiants/faculte_form.html', context)


@login_required
def faculte_update(request, pk):
    """
    Modifier une faculté
    """
    faculte = get_object_or_404(Faculte1, pk=pk)
    
    if request.method == 'POST':
        form = Faculte1Form(request.POST, instance=faculte)
        if form.is_valid():
            form.save()
            messages.success(request, f'La faculté "{faculte.nom}" a été modifiée avec succès.')
            return redirect('universite_detail', pk=faculte.universite.pk)
    else:
        form = Faculte1Form(instance=faculte)
    
    context = {
        'form': form,
        'faculte': faculte,
        'universite': faculte.universite,
        'titre': 'Modifier la faculté',
        'action': 'Modifier'
    }
    return render(request, 'bibliotheque/etudiants/faculte_form.html', context)


@login_required
def faculte_delete(request, pk):
    """
    Supprimer une faculté
    """
    faculte = get_object_or_404(Faculte1, pk=pk)
    universite_pk = faculte.universite.pk
    
    if request.method == 'POST':
        nom = faculte.nom
        faculte.delete()
        messages.success(request, f'La faculté "{nom}" a été supprimée avec succès.')
        return redirect('universite_detail', pk=universite_pk)
    
    context = {
        'faculte': faculte,
        'universite': faculte.universite,
    }
    return render(request, 'bibliotheque/etudiants/faculte_confirm_delete.html', context)


# ==================== DÉPARTEMENT ====================

@login_required
def departement_create(request, faculte_pk):
    """
    Créer un département pour une faculté
    """
    faculte = get_object_or_404(Faculte1, pk=faculte_pk)
    
    if request.method == 'POST':
        form = DepartementForm(request.POST)
        if form.is_valid():
            departement = form.save(commit=False)
            departement.faculte = faculte
            departement.save()
            messages.success(request, f'Le département "{departement.nom}" a été créé avec succès.')
            return redirect('universite_detail', pk=faculte.universite.pk)
    else:
        form = DepartementForm()
    
    context = {
        'form': form,
        'faculte': faculte,
        'universite': faculte.universite,
        'titre': 'Ajouter un département',
        'action': 'Créer'
    }
    return render(request, 'bibliotheque/etudiants/departement_form.html', context)


@login_required
def departement_update(request, pk):
    """
    Modifier un département
    """
    departement = get_object_or_404(Departement, pk=pk)
    
    if request.method == 'POST':
        form = DepartementForm(request.POST, instance=departement)
        if form.is_valid():
            form.save()
            messages.success(request, f'Le département "{departement.nom}" a été modifié avec succès.')
            return redirect('universite_detail', pk=departement.faculte.universite.pk)
    else:
        form = DepartementForm(instance=departement)
    
    context = {
        'form': form,
        'departement': departement,
        'faculte': departement.faculte,
        'universite': departement.faculte.universite,
        'titre': 'Modifier le département',
        'action': 'Modifier'
    }
    return render(request, 'bibliotheque/etudiants/departement_form.html', context)


@login_required
def departement_delete(request, pk):
    """
    Supprimer un département
    """
    departement = get_object_or_404(Departement, pk=pk)
    universite_pk = departement.faculte.universite.pk
    
    if request.method == 'POST':
        nom = departement.nom
        departement.delete()
        messages.success(request, f'Le département "{nom}" a été supprimé avec succès.')
        return redirect('universite_detail', pk=universite_pk)
    
    context = {
        'departement': departement,
        'faculte': departement.faculte,
        'universite': departement.faculte.universite,
    }
    return render(request, 'bibliotheque/etudiants/departement_confirm_delete.html', context)


# ==================== CLASSE ====================

@login_required
def classe_create(request, departement_pk):
    """
    Créer une classe pour un département
    """
    departement = get_object_or_404(Departement, pk=departement_pk)
    
    if request.method == 'POST':
        form = ClasseForm(request.POST)
        if form.is_valid():
            classe = form.save(commit=False)
            classe.departement = departement
            classe.save()
            messages.success(request, f'La classe "{classe.nom}" a été créée avec succès.')
            return redirect('universite_detail', pk=departement.faculte.universite.pk)
    else:
        form = ClasseForm()
    
    context = {
        'form': form,
        'departement': departement,
        'faculte': departement.faculte,
        'universite': departement.faculte.universite,
        'titre': 'Ajouter une classe',
        'action': 'Créer'
    }
    return render(request, 'bibliotheque/etudiants/classe_form.html', context)


@login_required
def classe_update(request, pk):
    """
    Modifier une classe
    """
    classe = get_object_or_404(Classe, pk=pk)
    
    if request.method == 'POST':
        form = ClasseForm(request.POST, instance=classe)
        if form.is_valid():
            form.save()
            messages.success(request, f'La classe "{classe.nom}" a été modifiée avec succès.')
            return redirect('universite_detail', pk=classe.departement.faculte.universite.pk)
    else:
        form = ClasseForm(instance=classe)
    
    context = {
        'form': form,
        'classe': classe,
        'departement': classe.departement,
        'faculte': classe.departement.faculte,
        'universite': classe.departement.faculte.universite,
        'titre': 'Modifier la classe',
        'action': 'Modifier'
    }
    return render(request, 'bibliotheque/etudiants/classe_form.html', context)


@login_required
def classe_delete(request, pk):
    """
    Supprimer une classe
    """
    classe = get_object_or_404(Classe, pk=pk)
    universite_pk = classe.departement.faculte.universite.pk
    
    if request.method == 'POST':
        nom = classe.nom
        classe.delete()
        messages.success(request, f'La classe "{nom}" a été supprimée avec succès.')
        return redirect('universite_detail', pk=universite_pk)
    
    context = {
        'classe': classe,
        'departement': classe.departement,
        'faculte': classe.departement.faculte,
        'universite': classe.departement.faculte.universite,
    }
    return render(request, 'bibliotheque/etudiants/classe_confirm_delete.html', context)


@login_required
def classe_detail(request, pk):
    """
    Détails d'une classe
    """
    classe = get_object_or_404(
        Classe.objects.select_related('departement__faculte__universite'),
        pk=pk
    )
    
    # Étudiants de la classe
    etudiants = Etudiant1.objects.filter(classe=classe).select_related(
        'universite', 'faculte', 'departement', 'classe'
    )
    
    context = {
        'classe': classe,
        'departement': classe.departement,
        'faculte': classe.departement.faculte,
        'universite': classe.departement.faculte.universite,
        'etudiants': etudiants,
        'nb_etudiants': etudiants.count(),
    }
    return render(request, 'bibliotheque/etudiants/classe_detail.html', context)

def valider_inscription(request, etudiant_id):
    """Permet à un admin de valider une inscription"""
    etudiant = get_object_or_404(Etudiant1, id=etudiant_id, statut='inactif')
    
    if request.method == 'POST':
        # Générer un matricule automatique
        dernier_matricule = Etudiant1.objects.filter(
            matricule__startswith='2025'
        ).count()
        etudiant.matricule = f"2025{str(dernier_matricule + 1).zfill(4)}"
        etudiant.statut = 'actif'
        etudiant.save()
        
        # Envoi d'email désactivé
        # send_mail(
        #     'Votre compte bibliothèque est activé',
        #     f'Bonjour {etudiant.prenom},\n\n'
        #     f'Votre inscription a été validée.\n'
        #     f'Votre matricule est: {etudiant.matricule}\n\n'
        #     f'Vous pouvez maintenant emprunter des livres.\n\n'
        #     f'Cordialement,',
        #     [etudiant.email],
        # )
        
        messages.success(request, f'Inscription de {etudiant.nom_complet} validée')
        return redirect('liste_inscriptions_en_attente')
    
    return render(request, 'bibliotheque/public/valider_inscription.html', {
        'etudiant': etudiant
    })
    
    
# def inscription_etudiant(request):
#     """Page d'inscription publique pour les étudiants"""
#     if request.method == 'POST':
#         form = InscriptionEtudiantForm(request.POST)
#         if form.is_valid():
#             etudiant = form.save(commit=False)
#             etudiant.statut = 'inactif'  # En attente de validation
#             etudiant.save()
            
#             # Envoi d'email désactivé
#             # try:
#             #     send_mail(
#             #         'Inscription à la bibliothèque',
#             #         f'Bonjour {etudiant.prenom} {etudiant.nom},\n\n'
#             #         f'Votre inscription a été reçue avec succès.\n'
#             #         f'Votre dossier sera traité dans les prochaines 48 heures.\n\n'
#             #         f'Cordialement,\nL\'équipe de la bibliothèque',
#             #         [etudiant.email],
#             #         fail_silently=True,
#             #     )
#             # except:
#             #     pass
            
#             messages.success(
#                 request, 
#                 'Votre inscription a été enregistrée avec succès ! '
#                 'Vous recevrez un email de confirmation une fois votre compte validé.'
#             )
#             return redirect('inscription_confirmation')
#         else:
#             messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
#     else:
#         form = InscriptionEtudiantForm()
    
#     return render(request, 'bibliotheque/public/inscription.html', {
#         'form': form,
#     })






def inscription_etudiant(request):
    """Page d'inscription publique pour les étudiants"""
    if request.method == 'POST':
        form = InscriptionEtudiantForm(request.POST)
        if form.is_valid():
            etudiant = form.save(commit=False)
            etudiant.statut = 'inactif'  # En attente de validation
            etudiant.save()
            
            # Envoi d'email désactivé
            # try:
            #     send_mail(...)
            # except:
            #     pass
            
            messages.success(
                request, 
                'Votre inscription a été enregistrée avec succès ! '
                'Veuillez vous connecter pour accéder à votre espace.'
            )
            # Redirection vers la page de connexion
            return redirect('login')  # ou le nom de votre URL de connexion
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = InscriptionEtudiantForm()
    
    return render(request, 'bibliotheque/public/inscription.html', {
        'form': form,
    })
    
    
def inscription_confirmation(request):
    """Page de confirmation après inscription"""
    return render(request, 'bibliotheque/public/inscription_confirmation.html')

# API pour charger les données hiérarchiques
from django.http import JsonResponse

def get_facultes_by_universite(request, universite_id):
    """Retourne les facultés d'une université"""
    facultes = Faculte1.objects.filter(universite_id=universite_id).values('id', 'nom')
    return JsonResponse(list(facultes), safe=False)

def get_departements_by_faculte(request, faculte_id):
    """Retourne les départements d'une faculté"""
    departements = Departement.objects.filter(faculte_id=faculte_id).values('id', 'nom')
    return JsonResponse(list(departements), safe=False)

def get_classes_by_departement(request, departement_id):
    """Retourne les classes d'un département"""
    classes = Classe.objects.filter(departement_id=departement_id).values('id', 'nom')
    return JsonResponse(list(classes), safe=False)