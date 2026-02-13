# bibliotheque/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from datetime import timedelta
from django.utils import timezone   
from django.core.exceptions import ValidationError
import requests
from django.conf import settings


from django.core.validators import MinValueValidator, MaxValueValidator

class ParametreBibliotheque(models.Model):
    """Paramètres généraux de la bibliothèque"""
    
    # Informations de base
    nom_bibliotheque = models.CharField(max_length=200, verbose_name="Nom de la bibliothèque")
    adresse = models.TextField(verbose_name="Adresse")
    telephone = models.CharField(max_length=20, verbose_name="Téléphone")
    email = models.EmailField(verbose_name="Email")
    site_web = models.URLField(blank=True, null=True, verbose_name="Site web")
    
    # Logo et image
    logo = models.ImageField(upload_to='bibliotheque/logos/', blank=True, null=True, verbose_name="Logo")
    
    # Horaires d'ouverture
    horaire_ouverture = models.TimeField(default="08:00", verbose_name="Heure d'ouverture")
    horaire_fermeture = models.TimeField(default="18:00", verbose_name="Heure de fermeture")
    jours_fermeture = models.CharField(
        max_length=100,
        default="Dimanche",
        verbose_name="Jours de fermeture",
        help_text="Séparer par des virgules (ex: Dimanche, Lundi)"
    )
    
    # Paramètres d'emprunt par défaut
    duree_emprunt_defaut = models.IntegerField(
        default=14,
        validators=[MinValueValidator(1), MaxValueValidator(90)],
        verbose_name="Durée d'emprunt par défaut (jours)"
    )
    nombre_emprunts_max = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name="Nombre maximum d'emprunts simultanés"
    )
    nombre_renouvellements_max = models.IntegerField(
        default=2,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name="Nombre maximum de renouvellements"
    )
    
    # Pénalités et amendes
    amende_par_jour = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.50,
        validators=[MinValueValidator(0)],
        verbose_name="Amende par jour de retard (€)"
    )
    amende_maximum = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=50.00,
        validators=[MinValueValidator(0)],
        verbose_name="Amende maximum (€)"
    )
    delai_suspension_apres_retard = models.IntegerField(
        default=30,
        validators=[MinValueValidator(0)],
        verbose_name="Délai de suspension après retard (jours)"
    )
    
    # Réservations
    duree_reservation_jours = models.IntegerField(
        default=7,
        validators=[MinValueValidator(1), MaxValueValidator(30)],
        verbose_name="Durée de validité d'une réservation (jours)"
    )
    nombre_reservations_max = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name="Nombre maximum de réservations simultanées"
    )
    
    # Notifications
    rappel_avant_echeance = models.IntegerField(
        default=3,
        validators=[MinValueValidator(0), MaxValueValidator(14)],
        verbose_name="Rappel avant échéance (jours)"
    )
    rappel_apres_retard = models.IntegerField(
        default=7,
        validators=[MinValueValidator(1), MaxValueValidator(30)],
        verbose_name="Rappel après retard (jours)"
    )
    
    # Carte de membre
    duree_validite_carte = models.IntegerField(
        default=365,
        validators=[MinValueValidator(30), MaxValueValidator(1825)],
        verbose_name="Durée de validité de la carte (jours)"
    )
    prix_carte = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=10.00,
        validators=[MinValueValidator(0)],
        verbose_name="Prix de la carte de membre (€)"
    )
    
    # Diverst
    age_minimum = models.IntegerField(
        default=16,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Âge minimum pour s'inscrire"
    )
    activer_notifications_email = models.BooleanField(
        default=True,
        verbose_name="Activer les notifications par email"
    )
    activer_notifications_sms = models.BooleanField(
        default=False,
        verbose_name="Activer les notifications par SMS"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    
    class Meta:
        verbose_name = "Paramètre de la bibliothèque"
        verbose_name_plural = "Paramètres de la bibliothèque"
    
    def __str__(self):
        return f"Paramètres - {self.nom_bibliotheque}"
    
    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y a qu'une seule instance
        if not self.pk and ParametreBibliotheque.objects.exists():
            raise ValueError("Il ne peut y avoir qu'une seule instance de paramètres")
        return super().save(*args, **kwargs)
    
    @classmethod
    def get_params(cls):
        """Récupérer ou créer les paramètres"""
        params, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'nom_bibliotheque': 'Bibliothèque Municipale',
                'adresse': 'Adresse à définir',
                'telephone': '0000000000',
                'email': 'contact@bibliotheque.com'
            }
        )
        return params


class CategorieEmprunteur(models.Model):
    """Catégories d'emprunteurs avec règles spécifiques"""
    
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom de la catégorie")
    description = models.TextField(blank=True, verbose_name="Description")
    
    # Règles spécifiques
    duree_emprunt = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(90)],
        verbose_name="Durée d'emprunt (jours)"
    )
    nombre_emprunts_max = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        verbose_name="Nombre maximum d'emprunts"
    )
    nombre_renouvellements = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name="Nombre de renouvellements autorisés"
    )
    
    # Tarification
    cotisation_annuelle = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Cotisation annuelle (Fbu)"
    )
    reduction_amende = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Réduction sur amendes (%)"
    )
    
    # Priorités
    priorite_reservation = models.BooleanField(
        default=False,
        verbose_name="Priorité sur les réservations"
    )
    acces_ressources_numeriques = models.BooleanField(
        default=True,
        verbose_name="Accès aux ressources numériques"
    )
    
    actif = models.BooleanField(default=True, verbose_name="Actif")
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Catégorie d'emprunteur"
        verbose_name_plural = "Catégories d'emprunteurs"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class JourFerie(models.Model):
    """Jours fériés et fermetures exceptionnelles"""
    
    nom = models.CharField(max_length=100, verbose_name="Nom du jour férié")
    date = models.DateField(verbose_name="Date")
    recurrent = models.BooleanField(
        default=True,
        verbose_name="Récurrent chaque année",
        help_text="Si coché, ce jour sera férié chaque année"
    )
    fermeture_totale = models.BooleanField(
        default=True,
        verbose_name="Fermeture totale",
        help_text="Si décoché, horaires réduits"
    )
    horaire_ouverture = models.TimeField(
        blank=True,
        null=True,
        verbose_name="Heure d'ouverture (si horaires réduits)"
    )
    horaire_fermeture = models.TimeField(
        blank=True,
        null=True,
        verbose_name="Heure de fermeture (si horaires réduits)"
    )
    
    class Meta:
        verbose_name = "Jour férié"
        verbose_name_plural = "Jours fériés"
        ordering = ['date']
    
    def __str__(self):
        return f"{self.nom} - {self.date.strftime('%d/%m/%Y')}"


class MessageSysteme(models.Model):
    """Messages système et annonces"""
    
    TYPE_CHOICES = [
        ('INFO', 'Information'),
        ('WARNING', 'Avertissement'),
        ('ERROR', 'Erreur'),
        ('SUCCESS', 'Succès'),
    ]
    
    CIBLE_CHOICES = [
        ('TOUS', 'Tous les utilisateurs'),
        ('ETUDIANTS', 'Étudiants uniquement'),
        ('PERSONNEL', 'Personnel uniquement'),
    ]
    
    titre = models.CharField(max_length=200, verbose_name="Titre")
    message = models.TextField(verbose_name="Message")
    type_message = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default='INFO',
        verbose_name="Type de message"
    )
    cible = models.CharField(
        max_length=20,
        choices=CIBLE_CHOICES,
        default='TOUS',
        verbose_name="Destinataires"
    )
    
    date_debut = models.DateTimeField(verbose_name="Date de début d'affichage")
    date_fin = models.DateTimeField(verbose_name="Date de fin d'affichage")
    
    actif = models.BooleanField(default=True, verbose_name="Actif")
    prioritaire = models.BooleanField(
        default=False,
        verbose_name="Message prioritaire",
        help_text="Sera affiché en haut de page"
    )
    
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Message système"
        verbose_name_plural = "Messages système"
        ordering = ['-prioritaire', '-date_debut']
    
    def __str__(self):
        return self.titre
    
    def est_actif(self):
        """Vérifie si le message doit être affiché"""
        now = timezone.now()
        return (
            self.actif and 
            self.date_debut <= now <= self.date_fin
        )


class RegleMetier(models.Model):
    """Règles métier personnalisables"""
    
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Code de la règle",
        help_text="Code unique pour identifier la règle"
    )
    nom = models.CharField(max_length=200, verbose_name="Nom de la règle")
    description = models.TextField(verbose_name="Description")
    
    actif = models.BooleanField(default=True, verbose_name="Règle active")
    
    # Valeur de la règle (peut être nombre, texte, booléen)
    valeur_numerique = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Valeur numérique"
    )
    valeur_texte = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Valeur texte"
    )
    valeur_boolean = models.BooleanField(
        blank=True,
        null=True,
        verbose_name="Valeur booléenne"
    )
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Règle métier"
        verbose_name_plural = "Règles métier"
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.nom}"


class ConfigurationEmail(models.Model):
    """Configuration des emails automatiques"""
    
    TYPE_EMAIL_CHOICES = [
        ('BIENVENUE', 'Email de bienvenue'),
        ('RAPPEL_ECHEANCE', 'Rappel avant échéance'),
        ('RETARD', 'Notification de retard'),
        ('RESERVATION_DISPONIBLE', 'Réservation disponible'),
        ('RENOUVELLEMENT', 'Confirmation de renouvellement'),
        ('ANNULATION', 'Annulation d\'emprunt/réservation'),
    ]
    
    type_email = models.CharField(
        max_length=50,
        choices=TYPE_EMAIL_CHOICES,
        unique=True,
        verbose_name="Type d'email"
    )
    sujet = models.CharField(max_length=200, verbose_name="Sujet")
    corps_message = models.TextField(
        verbose_name="Corps du message",
        help_text="Utilisez {nom}, {prenom}, {titre_livre}, {date_retour}, etc. pour personnaliser"
    )
    
    actif = models.BooleanField(default=True, verbose_name="Email actif")
    
    class Meta:
        verbose_name = "Configuration email"
        verbose_name_plural = "Configurations emails"
        ordering = ['type_email']
    
    def __str__(self):
        return f"{self.get_type_email_display()}"


class HistoriqueParametres(models.Model):
    """Historique des modifications des paramètres"""
    
    parametre_modifie = models.CharField(max_length=100, verbose_name="Paramètre modifié")
    ancienne_valeur = models.TextField(verbose_name="Ancienne valeur")
    nouvelle_valeur = models.TextField(verbose_name="Nouvelle valeur")
    
    date_modification = models.DateTimeField(auto_now_add=True)
    utilisateur = models.CharField(max_length=100, verbose_name="Utilisateur")
    
    class Meta:
        verbose_name = "Historique des paramètres"
        verbose_name_plural = "Historique des paramètres"
        ordering = ['-date_modification']
    
    def __str__(self):
        return f"{self.parametre_modifie} - {self.date_modification.strftime('%d/%m/%Y %H:%M')}"

class Universite(models.Model):
    """Universités partenaires"""
    nom = models.CharField(max_length=200, unique=True)
    adresse = models.TextField()
    ville = models.CharField(max_length=100)
    pays = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    site_web = models.URLField(blank=True, null=True)
    date_partenariat = models.DateField()
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Université"
        verbose_name_plural = "Universités"
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Auteur(models.Model):
    """Auteurs de livres"""
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField(null=True, blank=True)
    nationalite = models.CharField(max_length=100, blank=True)
    biographie = models.TextField(blank=True)
    # photo = models.ImageField(upload_to='auteurs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Auteur"
        verbose_name_plural = "Auteurs"
        ordering = ['nom', 'prenom']
        unique_together = ['nom', 'prenom']

    def __str__(self):
        return f"{self.nom} {self.prenom}"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"


class Etagere(models.Model):
    """Étagères physiques de la bibliothèque"""
    code = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=200)
    salle = models.CharField(max_length=50)
    etage = models.IntegerField()
    capacite_max = models.IntegerField(validators=[MinValueValidator(1)])
    # taux_remplissage=models.IntegerField(validators=[MinValueValidator(2)])
    created_at = models.DateTimeField(auto_now_add=True)
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Étagère"
        verbose_name_plural = "Étagères"
        ordering = ['etage', 'code']

    def __str__(self):
        return f"{self.code} - {self.salle}"

    @property
    def nombre_livres(self):
        return Livre.objects.filter(emplacement__compartiment__etagere=self).count()


class Compartiment(models.Model):
    """Compartiments dans une étagère"""
    etagere = models.ForeignKey(Etagere, on_delete=models.CASCADE, related_name='compartiments')
    numero = models.IntegerField()
    niveau = models.CharField(max_length=50, help_text="Niveau du compartiment (haut, milieu, bas)")
    categorie = models.CharField(max_length=100, blank=True, help_text="Catégorie des livres")
    capacite = models.IntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Compartiment"
        verbose_name_plural = "Compartiments"
        ordering = ['etagere', 'numero']
        unique_together = ['etagere', 'numero']

    def __str__(self):
        return f"{self.etagere.code} - Compartiment {self.numero}"

    @property
    def est_plein(self):
        return self.emplacements.count() >= self.capacite


class EmplacementLivre(models.Model):
    """Emplacement physique d'un livre"""
    compartiment = models.ForeignKey(Compartiment, on_delete=models.CASCADE, related_name='emplacements')
    position = models.IntegerField()
    code_emplacement = models.CharField(max_length=50, unique=True)
    disponible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Emplacement"
        verbose_name_plural = "Emplacements"
        ordering = ['compartiment', 'position']
        unique_together = ['compartiment', 'position']

    def __str__(self):
        return self.code_emplacement


class Livre(models.Model):
    """Livres de la bibliothèque"""
    LANGUES = [
        ('FR', 'Français'),
        ('EN', 'Anglais'),
        ('ES', 'Espagnol'),
        ('DE', 'Allemand'),
        ('IT', 'Italien'),
        ('AR', 'Arabe'),
        ('OTHER', 'Autre'),
    ]

    ETATS = [
        ('NEUF', 'Neuf'),
        ('BON', 'Bon état'),
        ('MOYEN', 'État moyen'),
        ('MAUVAIS', 'Mauvais état'),
    ]

    isbn = models.CharField(max_length=13, unique=True, help_text="ISBN à 13 chiffres")
    titre = models.CharField(max_length=300)
    sous_titre = models.CharField(max_length=300, blank=True)
    auteurs = models.ManyToManyField(Auteur, related_name='livres')
    editeur = models.CharField(max_length=200)
    annee_publication = models.IntegerField()
    nombre_pages = models.IntegerField(validators=[MinValueValidator(1)])
    langue = models.CharField(max_length=10, choices=LANGUES, default='FR')
    categorie = models.CharField(max_length=100)
    resume = models.TextField(blank=True)
    couverture = models.ImageField(upload_to='couvertures/', blank=True, null=True)
    nombre_exemplaires = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    etat = models.CharField(max_length=10, choices=ETATS, default='BON')
    emplacement = models.ForeignKey(EmplacementLivre, on_delete=models.SET_NULL, null=True, blank=True, related_name='livres')
    disponible = models.BooleanField(default=True)
    version_numerique = models.FileField(upload_to='livres_numeriques/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Livre"
        verbose_name_plural = "Livres"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['isbn']),
            models.Index(fields=['titre']),
            models.Index(fields=['categorie']),
        ]

    def __str__(self):
        return self.titre

    @property
    def auteurs_liste(self):
        return ", ".join([str(a) for a in self.auteurs.all()])

    @property
    def exemplaires_disponibles(self):
        emprunts_actifs = self.emprunts.filter(date_retour_effective__isnull=True).count()
        return self.nombre_exemplaires - emprunts_actifs


class Personnel(models.Model):
    """Personnel de la bibliothèque"""
    ROLES = [
        ('BIBLIOTHECAIRE', 'Bibliothécaire'),
        ('ASSISTANT', 'Assistant'),
        ('DIRECTEUR', 'Directeur'),
        ('TECHNICIEN', 'Technicien'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='personnel')
    matricule = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20)
    role = models.CharField(max_length=20, choices=ROLES)
    universite = models.ForeignKey(Universite, on_delete=models.CASCADE, related_name='personnel')
    date_embauche = models.DateField()
    actif = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='personnel/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Personnel"
        verbose_name_plural = "Personnel"
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.get_role_display()}"


class Etudiant(models.Model):
    """Abonne.es"""
    NIVEAUX = [
        ('L1', 'Licence 1'),
        ('L2', 'Licence 2'),
        ('L3', 'Licence 3'),
        ('M1', 'Master 1'),
        ('M2', 'Master 2'),
        ('DOCTORAT', 'Doctorat'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='etudiant')
    numero_etudiant = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20)
    date_naissance = models.DateField()
    universite = models.ForeignKey(Universite, on_delete=models.CASCADE, related_name='etudiants')
    faculte = models.CharField(max_length=200)
    departement = models.CharField(max_length=200)
    niveau = models.CharField(max_length=10, choices=NIVEAUX)
    annee_inscription = models.CharField(max_length=11)
    photo = models.ImageField(upload_to='etudiants/', blank=True, null=True)
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Étudiant"
        verbose_name_plural = "Étudiants"
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.numero_etudiant}"

    @property
    def a_abonnement_actif(self):
        return self.abonnements.filter(actif=True, date_fin__gte=timezone.now().date()).exists()


class Abonnement(models.Model):
    """Abonnements des étudiants"""
    TYPES = [
        ('MENSUEL', 'Mensuel'),
        ('TRIMESTRIEL', 'Trimestriel'),
        ('SEMESTRIEL', 'Semestriel'),
        ('ANNUEL', 'Annuel'),
    ]

    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='abonnements')
    type_abonnement = models.CharField(max_length=15, choices=TYPES)
    date_debut = models.DateField()
    date_fin = models.DateField()
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    actif = models.BooleanField(default=True)
    nombre_emprunts_max = models.IntegerField(default=5)
    duree_emprunt_jours = models.IntegerField(default=14)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Abonnement"
        verbose_name_plural = "Abonnements"
        ordering = ['-date_debut']

    def __str__(self):
        return f"{self.etudiant} - {self.get_type_abonnement_display()}"

    @property
    def est_expire(self):
        return timezone.now().date() > self.date_fin

    @property
    def jours_restants(self):
        if self.est_expire:
            return 0
        return (self.date_fin - timezone.now().date()).days


class Emprunt(models.Model):
    """Emprunts de livres"""
    STATUTS = [
        ('EN_COURS', 'En cours'),
        ('RETOURNE', 'Retourné'),
        ('EN_RETARD', 'En retard'),
        ('PERDU', 'Perdu'),
    ]

    livre = models.ForeignKey(Livre, on_delete=models.CASCADE, related_name='emprunts')
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='emprunts')
    personnel = models.ForeignKey(Personnel, on_delete=models.SET_NULL, null=True, related_name='emprunts_traites')
    remarques = models.TextField(blank=True, null=True)
    date_emprunt = models.DateTimeField(auto_now_add=True)
    date_retour_prevue = models.DateField()
    date_retour_effective = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=15, choices=STATUTS, default='EN_COURS')
    penalite = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Emprunt"
        verbose_name_plural = "Emprunts"
        ordering = ['-date_emprunt']
        indexes = [
            models.Index(fields=['statut']),
            models.Index(fields=['date_retour_prevue']),
        ]

    def __str__(self):
        return f"{self.livre.titre} - {self.etudiant.nom}"

    @property
    def est_en_retard(self):
        if self.date_retour_effective:
            return False
        return timezone.now().date() > self.date_retour_prevue

    @property
    def jours_retard(self):
        if not self.est_en_retard:
            return 0
        return (timezone.now().date() - self.date_retour_prevue).days

    def save(self, *args, **kwargs):
        if not self.date_retour_prevue:
            abonnement = self.etudiant.abonnements.filter(actif=True).first()
            if abonnement:
                self.date_retour_prevue = timezone.now().date() + timedelta(days=abonnement.duree_emprunt_jours)
            else:
                self.date_retour_prevue = timezone.now().date() + timedelta(days=14)
        
        if self.est_en_retard and self.statut == 'EN_COURS':
            self.statut = 'EN_RETARD'
        
        super().save(*args, **kwargs)


class Reservation(models.Model):
    """Réservations de livres"""
    STATUTS = [
        ('EN_ATTENTE', 'En attente'),
        ('PRETE', 'Prêt à retirer'),
        ('ANNULEE', 'Annulée'),
        ('EXPIREE', 'Expirée'),
    ]

    livre = models.ForeignKey(Livre, on_delete=models.CASCADE, related_name='reservations')
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='reservations')
    date_reservation = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateField()
    statut = models.CharField(max_length=15, choices=STATUTS, default='EN_ATTENTE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"
        ordering = ['-date_reservation']

    def __str__(self):
        return f"{self.livre.titre} - {self.etudiant.nom}"


class Notification(models.Model):
    """Notifications pour les utilisateurs"""
    TYPES = [
        ('RAPPEL', 'Rappel de retour'),
        ('RETARD', 'Retard'),
        ('RESERVATION', 'Réservation disponible'),
        ('ABONNEMENT', 'Abonnement'),
    ]

    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='notifications')
    type_notification = models.CharField(max_length=15, choices=TYPES)
    message = models.TextField()
    lu = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_type_notification_display()} - {self.etudiant}"
    


class Universite1(models.Model):
    """Modèle pour les universités"""
    nom = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    adresse = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Université"
        verbose_name_plural = "Universités"
    
    def __str__(self):
        return self.nom


class Faculte1(models.Model):
    nom = models.CharField(max_length=200)
    code = models.CharField(max_length=50)  # Sans unique
    sigle = models.CharField(max_length=20, default='N/A')
    universite = models.ForeignKey(Universite, on_delete=models.CASCADE, related_name='facultes')
    
    class Meta:
        verbose_name = "Faculté"
        verbose_name_plural = "Facultés"
        # Retirer unique_together si non nécessaire
    
    def __str__(self):
        return f"{self.nom} - {self.universite.nom}"


class Departement(models.Model):
    nom = models.CharField(max_length=200)
    code = models.CharField(max_length=50)
    sigle = models.CharField(max_length=20, default='N/A')  # Ajoutez cette ligne
    universite = models.ForeignKey(
        Universite, 
        on_delete=models.CASCADE, 
        related_name='departements',
        null=True,  # <-- Temporairement nullable
        blank=True
    )
    faculte = models.ForeignKey(
        Faculte1, 
        on_delete=models.CASCADE, 
        related_name='departements',
        null=True,  # <-- Temporairement nullable
        blank=True
    )
    class Meta:
        verbose_name = "Département"
        verbose_name_plural = "Départements"
    
    def __str__(self):
        return f"{self.nom} - {self.faculte.nom}"


class Classe(models.Model):
    """Modèle pour les classes/promotions"""
    nom = models.CharField(max_length=100)
    niveau = models.CharField(max_length=50)  # Ex: L1, L2, L3, M1, M2
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE, related_name='classes', null=True, blank=True)
    faculte = models.ForeignKey(Faculte1, on_delete=models.CASCADE, related_name='classes', null=True, blank=True)
    annee_academique = models.CharField(max_length=20)  # Ex: 2024-2025
    
    class Meta:
        verbose_name = "Classe"
        verbose_name_plural = "Classes"
    
    def __str__(self):
        return f"{self.nom} - {self.niveau} ({self.annee_academique})"


class Etudiant1(models.Model):
    """Modèle pour les étudiants récupérés via API"""
    
    # Identifiants
    matricule = models.CharField(max_length=50, unique=True, db_index=True)
    api_id = models.CharField(max_length=100, unique=True, null=True, blank=True, 
                             help_text="ID de l'étudiant dans le système externe")
    
    # Informations personnelles
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField(null=True, blank=True)
    lieu_naissance = models.CharField(max_length=200, blank=True)
    sexe = models.CharField(max_length=1, choices=[('M', 'Masculin'), ('F', 'Féminin')], blank=True)
    
    
    
   
    # Contact
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True)
    
    # Hiérarchie académique
    universite = models.ForeignKey(Universite, on_delete=models.PROTECT, related_name='etudiants1')
    faculte = models.ForeignKey(Faculte1, on_delete=models.SET_NULL, null=True, blank=True, related_name='etudiants1')
    departement = models.ForeignKey(Departement, on_delete=models.SET_NULL, null=True, blank=True, related_name='etudiants1')
    classe = models.ForeignKey(Classe, on_delete=models.SET_NULL, null=True, blank=True, related_name='etudiants1')
    
     
    # Informations académiques
    niveau_etude = models.CharField(max_length=50, blank=True)  # L1, L2, M1, etc.
    annee_academique = models.CharField(max_length=20, blank=True)
    statut = models.CharField(max_length=20, 
                             choices=[
                                 ('actif', 'Actif'),
                                 ('inactif', 'Inactif'),
                                 ('suspendu', 'Suspendu'),
                                 ('diplome', 'Diplômé')
                             ],
                             default='actif')
    
    # Métadonnées de synchronisation
    sync_depuis_api = models.BooleanField(default=True, help_text="Indique si l'étudiant provient de l'API")
    derniere_sync = models.DateTimeField(auto_now=True, help_text="Date de dernière synchronisation avec l'API")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    # Données brutes de l'API (optionnel, pour debug)
    donnees_api_brutes = models.JSONField(null=True, blank=True, 
                                         help_text="Données brutes reçues de l'API")
    
    class Meta:
        verbose_name = "Étudiant (API)"
        verbose_name_plural = "Étudiants (API)"
        ordering = ['nom', 'prenom']
        indexes = [
            models.Index(fields=['matricule']),
            models.Index(fields=['email']),
            models.Index(fields=['universite', 'faculte']),
        ]
    
    def __str__(self):
        return f"{self.matricule} - {self.nom} {self.prenom}"
    
    def clean(self):
        """Validation personnalisée"""
        super().clean()
        
        # Vérifier la cohérence de la hiérarchie
        if self.faculte and self.faculte.universite != self.universite:
            raise ValidationError("La faculté doit appartenir à l'université sélectionnée")
        
        if self.departement:
            if self.faculte and self.departement.faculte != self.faculte:
                raise ValidationError("Le département doit appartenir à la faculté sélectionnée")
            if self.departement.universite != self.universite:
                raise ValidationError("Le département doit appartenir à l'université sélectionnée")
        
        if self.classe:
            if self.departement and self.classe.departement != self.departement:
                raise ValidationError("La classe doit appartenir au département sélectionné")
            if self.faculte and self.classe.faculte != self.faculte:
                raise ValidationError("La classe doit appartenir à la faculté sélectionnée")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def nom_complet(self):
        """Retourne le nom complet de l'étudiant"""
        return f"{self.nom} {self.prenom}"
    
    @property
    def parcours_academique(self):
        """Retourne le parcours académique complet"""
        parcours = [self.universite.nom]
        if self.faculte:
            parcours.append(self.faculte.nom)
        if self.departement:
            parcours.append(self.departement.nom)
        if self.classe:
            parcours.append(self.classe.nom)
        return " > ".join(parcours)
    
    @classmethod
    def recuperer_depuis_api(cls, matricule=None, api_id=None, email=None):
        """
        Récupère un étudiant depuis l'API externe et le crée/met à jour dans la base
        
        Args:
            matricule: Matricule de l'étudiant
            api_id: ID de l'étudiant dans le système externe
            email: Email de l'étudiant
        
        Returns:
            Instance de Etudiant1 ou None si non trouvé
        """
        # Configuration de l'API (à adapter selon votre API)
        api_url = getattr(settings, 'ETUDIANT_API_URL', None)
        api_key = getattr(settings, 'ETUDIANT_API_KEY', None)
        
        if not api_url:
            raise ValueError("ETUDIANT_API_URL n'est pas configuré dans settings.py")
        
        # Construire les paramètres de recherche
        params = {}
        if matricule:
            params['matricule'] = matricule
        if api_id:
            params['id'] = api_id
        if email:
            params['email'] = email
        
        if not params:
            raise ValueError("Au moins un paramètre de recherche doit être fourni")
        
        # Appel à l'API
        headers = {'Authorization': f'Bearer {api_key}'} if api_key else {}
        
        try:
            response = requests.get(
                f"{api_url}/etudiants/",
                params=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if not data or (isinstance(data, list) and len(data) == 0):
                return None
            
            # Si l'API retourne une liste, prendre le premier élément
            etudiant_data = data[0] if isinstance(data, list) else data
            
            # Créer ou mettre à jour l'étudiant
            return cls.creer_ou_mettre_a_jour_depuis_api(etudiant_data)
            
        except requests.RequestException as e:
            raise Exception(f"Erreur lors de la récupération depuis l'API: {str(e)}")
    
    @classmethod
    def creer_ou_mettre_a_jour_depuis_api(cls, donnees_api):
        """
        Crée ou met à jour un étudiant à partir des données API
        
        Args:
            donnees_api: Dictionnaire contenant les données de l'étudiant
        
        Returns:
            Instance de Etudiant1
        """
        # Récupérer ou créer l'université
        universite, _ = Universite.objects.get_or_create(
            code=donnees_api.get('universite_code'),
            defaults={'nom': donnees_api.get('universite_nom', 'Université Inconnue')}
        )
        
        # Récupérer ou créer la faculté si présente
        faculte = None
        if donnees_api.get('faculte_code'):
            faculte, _ = Faculte1.objects.get_or_create(
                code=donnees_api['faculte_code'],
                universite=universite,
                defaults={'nom': donnees_api.get('faculte_nom', 'Faculté Inconnue')}
            )
        
        # Récupérer ou créer le département si présent
        departement = None
        if donnees_api.get('departement_code'):
            departement, _ = Departement.objects.get_or_create(
                code=donnees_api['departement_code'],
                universite=universite,
                defaults={
                    'nom': donnees_api.get('departement_nom', 'Département Inconnu'),
                    'faculte': faculte
                }
            )
        
        # Récupérer ou créer la classe si présente
        classe = None
        if donnees_api.get('classe_nom'):
            classe, _ = Classe.objects.get_or_create(
                nom=donnees_api['classe_nom'],
                niveau=donnees_api.get('niveau', ''),
                annee_academique=donnees_api.get('annee_academique', ''),
                defaults={
                    'departement': departement,
                    'faculte': faculte
                }
            )
        
        # Créer ou mettre à jour l'étudiant
        etudiant, created = cls.objects.update_or_create(
            matricule=donnees_api['matricule'],
            defaults={
                'api_id': donnees_api.get('id'),
                'nom': donnees_api['nom'],
                'prenom': donnees_api['prenom'],
                'email': donnees_api['email'],
                'telephone': donnees_api.get('telephone', ''),
                'date_naissance': donnees_api.get('date_naissance'),
                'lieu_naissance': donnees_api.get('lieu_naissance', ''),
                'sexe': donnees_api.get('sexe', ''),
                'adresse': donnees_api.get('adresse', ''),
                'universite': universite,
                'faculte': faculte,
                'departement': departement,
                'classe': classe,
                'niveau_etude': donnees_api.get('niveau', ''),
                'annee_academique': donnees_api.get('annee_academique', ''),
                'statut': donnees_api.get('statut', 'actif'),
                'sync_depuis_api': True,
                'donnees_api_brutes': donnees_api
            }
        )
        
        return etudiant
    
    @classmethod
    def rechercher_pour_emprunt(cls, recherche):
        """
        Recherche un étudiant pour un emprunt de livre
        Cherche d'abord dans la base, puis dans l'API si non trouvé
        
        Args:
            recherche: Matricule, email ou nom de l'étudiant
        
        Returns:
            Instance de Etudiant1 ou None
        """
        # Recherche dans la base locale
        etudiant = None
        
        # Recherche par matricule
        if recherche:
            etudtiant = cls.objects.filter(
                models.Q(matricule__iexact=recherche) |
                models.Q(email__iexact=recherche) |
                models.Q(nom__icontains=recherche) |
                models.Q(prenom__icontains=recherche)
            ).first()
        
        # Si non trouvé localement, chercher dans l'API
        if not etudiant:
            try:
                # Essayer par matricule
                etudiant = cls.recuperer_depuis_api(matricule=recherche)
                
                # Si pas trouvé, essayer par email
                if not etudiant and '@' in recherche:
                    etudiant = cls.recuperer_depuis_api(email=recherche)
                    
            except Exception as e:
                # Logger l'erreur mais ne pas bloquer
                print(f"Erreur lors de la recherche API: {str(e)}")
        
        return etudiant
    
    def peut_emprunter(self):
        """Vérifie si l'étudiant peut emprunter des livres"""
        return self.statut == 'actif'