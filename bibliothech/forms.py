# bibliotheque/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from .models import (
    Universite, Auteur, Etagere, Compartiment, EmplacementLivre,
    Livre, Personnel, Etudiant, Abonnement, Emprunt, Reservation, Notification
)
from .models import Etudiant1, Emprunt, Livre
from .models import (
    ParametreBibliotheque,
    CategorieEmprunteur,
    JourFerie,
    MessageSysteme,
    RegleMetier,
    ConfigurationEmail,
)



# ==================== FORMULAIRES D'AUTHENTIFICATION ====================

class CustomUserCreationForm(UserCreationForm):
    """Formulaire d'inscription personnalisé"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    first_name = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prénom'
        })
    )
    last_name = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom d\'utilisateur'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmer le mot de passe'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Cet email est déjà utilisé.")
        return email


class CustomAuthenticationForm(AuthenticationForm):
    """Formulaire de connexion personnalisé"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom d\'utilisateur',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class CustomPasswordChangeForm(PasswordChangeForm):
    """Formulaire de changement de mot de passe personnalisé"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ancien mot de passe'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nouveau mot de passe'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmer le nouveau mot de passe'
        })


# ==================== FORMULAIRES DES MODÈLES ====================

class UniversiteForm(forms.ModelForm):
    """Formulaire pour les universités"""
    class Meta:
        model = Universite
        fields = [
            'nom', 'adresse', 'ville', 'pays', 'email', 
            'telephone', 'site_web', 'date_partenariat', 'actif'
        ]
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'pays': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'site_web': forms.URLInput(attrs={'class': 'form-control'}),
            'date_partenariat': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AuteurForm(forms.ModelForm):
    """Formulaire pour les auteurs"""
    class Meta:
        model = Auteur
        fields = ['nom', 'prenom', 'date_naissance', 'nationalite', 'biographie']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'nationalite': forms.TextInput(attrs={'class': 'form-control'}),
            'biographie': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class EtagereForm(forms.ModelForm):
    """Formulaire pour les étagères"""
    class Meta:
        model = Etagere
        fields = ['code', 'description', 'salle', 'etage', 'capacite_max']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'salle': forms.TextInput(attrs={'class': 'form-control'}),
            'etage': forms.NumberInput(attrs={'class': 'form-control'}),
            'capacite_max': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class CompartimentForm(forms.ModelForm):
    """Formulaire pour les compartiments"""
    class Meta:
        model = Compartiment
        fields = ['etagere', 'numero', 'niveau', 'categorie', 'capacite']
        widgets = {
            'etagere': forms.Select(attrs={'class': 'form-control'}),
            'numero': forms.NumberInput(attrs={'class': 'form-control'}),
            'niveau': forms.TextInput(attrs={'class': 'form-control'}),
            'categorie': forms.TextInput(attrs={'class': 'form-control'}),
            'capacite': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class EmplacementLivreForm(forms.ModelForm):
    """Formulaire pour les emplacements de livres"""
    class Meta:
        model = EmplacementLivre
        fields = ['compartiment', 'position', 'code_emplacement', 'disponible']
        widgets = {
            'compartiment': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.NumberInput(attrs={'class': 'form-control'}),
            'code_emplacement': forms.TextInput(attrs={'class': 'form-control'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class LivreForm(forms.ModelForm):
    """Formulaire pour les livres"""
    class Meta:
        model = Livre
        fields = [
            'isbn', 'titre', 'sous_titre', 'auteurs', 'editeur',
            'annee_publication', 'nombre_pages', 'langue', 'categorie',
            'resume', 'couverture', 'nombre_exemplaires', 'etat',
            'emplacement', 'disponible', 'version_numerique'
        ]
        widgets = {
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'sous_titre': forms.TextInput(attrs={'class': 'form-control'}),
            'auteurs': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'editeur': forms.TextInput(attrs={'class': 'form-control'}),
            'annee_publication': forms.NumberInput(attrs={'class': 'form-control'}),
            'nombre_pages': forms.NumberInput(attrs={'class': 'form-control'}),
            'langue': forms.Select(attrs={'class': 'form-control'}),
            'categorie': forms.TextInput(attrs={'class': 'form-control'}),
            'resume': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'couverture': forms.FileInput(attrs={'class': 'form-control'}),
            'nombre_exemplaires': forms.NumberInput(attrs={'class': 'form-control'}),
            'etat': forms.Select(attrs={'class': 'form-control'}),
            'emplacement': forms.Select(attrs={'class': 'form-control'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'version_numerique': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn')
        if isbn and not isbn.isdigit():
            raise ValidationError("L'ISBN doit contenir uniquement des chiffres.")
        if isbn and len(isbn) != 13:
            raise ValidationError("L'ISBN doit contenir exactement 13 chiffres.")
        return isbn


class PersonnelForm(forms.ModelForm):
    """Formulaire pour le personnel"""
    class Meta:
        model = Personnel
        fields = [
            'matricule', 'nom', 'prenom', 'email', 'telephone',
            'role', 'universite', 'date_embauche', 'actif', 'photo'
        ]
        widgets = {
            'matricule': forms.TextInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'universite': forms.Select(attrs={'class': 'form-control'}),
            'date_embauche': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class EtudiantForm(forms.ModelForm):
    """Formulaire pour les étudiants"""
    class Meta:
        model = Etudiant
        fields = [
            'numero_etudiant', 'nom', 'prenom', 'email', 'telephone',
            'date_naissance', 'universite', 'faculte', 'departement',
            'niveau', 'annee_inscription', 'photo', 'actif'
        ]
        widgets = {
            'numero_etudiant': forms.TextInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'universite': forms.Select(attrs={'class': 'form-control'}),
            'faculte': forms.TextInput(attrs={'class': 'form-control'}),
            'departement': forms.TextInput(attrs={'class': 'form-control'}),
            'niveau': forms.Select(attrs={'class': 'form-control'}),
            'annee_inscription': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AbonnementForm(forms.ModelForm):
    """Formulaire pour les abonnements"""
    class Meta:
        model = Abonnement
        fields = [
            'etudiant', 'type_abonnement', 'date_debut', 'date_fin',
            'montant', 'actif', 'nombre_emprunts_max', 'duree_emprunt_jours'
        ]
        widgets = {
            'etudiant': forms.Select(attrs={'class': 'form-control'}),
            'type_abonnement': forms.Select(attrs={'class': 'form-control'}),
            'date_debut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'nombre_emprunts_max': forms.NumberInput(attrs={'class': 'form-control'}),
            'duree_emprunt_jours': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')

        if date_debut and date_fin and date_debut >= date_fin:
            raise ValidationError("La date de fin doit être après la date de début.")

        return cleaned_data


class EmpruntForm(forms.ModelForm):
    """Formulaire pour les emprunts"""
    class Meta:
        model = Emprunt
        fields = [
            'livre', 'etudiant', 'personnel', 'date_retour_prevue',
            'date_retour_effective', 'statut', 'penalite', 'notes'
        ]
        widgets = {
            'livre': forms.Select(attrs={'class': 'form-control'}),
            'etudiant': forms.Select(attrs={'class': 'form-control'}),
            'personnel': forms.Select(attrs={'class': 'form-control'}),
            'date_retour_prevue': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_retour_effective': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'penalite': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        livre = cleaned_data.get('livre')
        etudiant = cleaned_data.get('etudiant')

        if livre and livre.exemplaires_disponibles <= 0:
            raise ValidationError("Ce livre n'a plus d'exemplaires disponibles.")

        if etudiant and not etudiant.a_abonnement_actif:
            raise ValidationError("Cet étudiant n'a pas d'abonnement actif.")

        # Vérifier le nombre d'emprunts actifs
        if etudiant:
            abonnement = etudiant.abonnements.filter(actif=True).first()
            if abonnement:
                emprunts_actifs = etudiant.emprunts.filter(
                    date_retour_effective__isnull=True
                ).count()
                if emprunts_actifs >= abonnement.nombre_emprunts_max:
                    raise ValidationError(
                        f"Cet étudiant a atteint le nombre maximum d'emprunts ({abonnement.nombre_emprunts_max})."
                    )

        return cleaned_data


class ReservationForm(forms.ModelForm):
    """Formulaire pour les réservations"""
    class Meta:
        model = Reservation
        fields = ['livre', 'etudiant', 'date_expiration', 'statut']
        widgets = {
            'livre': forms.Select(attrs={'class': 'form-control'}),
            'etudiant': forms.Select(attrs={'class': 'form-control'}),
            'date_expiration': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            # Par défaut, la réservation expire dans 3 jours
            self.fields['date_expiration'].initial = (
                timezone.now().date() + timedelta(days=3)
            )


class NotificationForm(forms.ModelForm):
    """Formulaire pour les notifications"""
    class Meta:
        model = Notification
        fields = ['etudiant', 'type_notification', 'message', 'lu']
        widgets = {
            'etudiant': forms.Select(attrs={'class': 'form-control'}),
            'type_notification': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'lu': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# ==================== FORMULAIRES DE RECHERCHE ====================

class RechercherLivreForm(forms.Form):
    """Formulaire de recherche de livres"""
    recherche = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Titre, auteur, ISBN...'
        })
    )
    categorie = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Catégorie'
        })
    )
    langue = forms.ChoiceField(
        required=False,
        choices=[('', 'Toutes')] + Livre.LANGUES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    disponible = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class RechercherEtudiantForm(forms.Form):
    """Formulaire de recherche d'étudiants"""
    recherche = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom, prénom, numéro...'
        })
    )
    universite = forms.ModelChoiceField(
        required=False,
        queryset=Universite.objects.filter(actif=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='Toutes les universités'
    )
    niveau = forms.ChoiceField(
        required=False,
        choices=[('', 'Tous')] + Etudiant.NIVEAUX,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    actif = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    


class ParametreBibliothequeForm(forms.ModelForm):
    class Meta:
        model = ParametreBibliotheque
        fields = "__all__"
        widgets = {
            "adresse": forms.Textarea(attrs={"rows": 3}),
            "jours_fermeture": forms.TextInput(
                attrs={"placeholder": "Ex: Dimanche, Lundi"}
            ),
            "horaire_ouverture": forms.TimeInput(format="%H:%M"),
            "horaire_fermeture": forms.TimeInput(format="%H:%M"),
        }


class CategorieEmprunteurForm(forms.ModelForm):
    class Meta:
        model = CategorieEmprunteur
        fields = "__all__"
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class JourFerieForm(forms.ModelForm):
    class Meta:
        model = JourFerie
        fields = "__all__"
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "horaire_ouverture": forms.TimeInput(format="%H:%M"),
            "horaire_fermeture": forms.TimeInput(format="%H:%M"),
        }

    def clean(self):
        cleaned_data = super().clean()
        fermeture_totale = cleaned_data.get("fermeture_totale")
        ouverture = cleaned_data.get("horaire_ouverture")
        fermeture = cleaned_data.get("horaire_fermeture")

        if not fermeture_totale and (not ouverture or not fermeture):
            raise forms.ValidationError(
                "Les horaires sont obligatoires si la fermeture n'est pas totale."
            )
        return cleaned_data


class MessageSystemeForm(forms.ModelForm):
    class Meta:
        model = MessageSysteme
        fields = "__all__"
        widgets = {
            "message": forms.Textarea(attrs={"rows": 4}),
            "date_debut": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "date_fin": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get("date_debut")
        date_fin = cleaned_data.get("date_fin")

        if date_debut and date_fin and date_fin < date_debut:
            raise forms.ValidationError(
                "La date de fin doit être postérieure à la date de début."
            )
        return cleaned_data


class RegleMetierForm(forms.ModelForm):
    class Meta:
        model = RegleMetier
        fields = "__all__"
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        valeurs = [
            cleaned_data.get("valeur_numerique"),
            cleaned_data.get("valeur_texte"),
            cleaned_data.get("valeur_boolean"),
        ]

        if sum(v is not None for v in valeurs) != 1:
            raise forms.ValidationError(
                "Vous devez renseigner une seule valeur (numérique, texte ou booléenne)."
            )
        return cleaned_data


class ConfigurationEmailForm(forms.ModelForm):
    class Meta:
        model = ConfigurationEmail
        fields = "__all__"
        widgets = {
            "corps_message": forms.Textarea(attrs={"rows": 6}),
        }
        
        


#======================RECUPERATION D'UN ETUDIANT VIA AUX APIS=====================



class RechercheEtudiantForm(forms.Form):
    """Formulaire de recherche d'étudiant"""
    q = forms.CharField(
        label='Rechercher un étudiant',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Matricule, nom, prénom ou email...',
            'autofocus': True
        })
    )
    
    recherche_api = forms.BooleanField(
        label='Rechercher aussi dans l\'API externe',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class EmpruntForm(forms.ModelForm):
    """Formulaire pour créer un emprunt"""
    
    class Meta:
        model = Emprunt
        fields = ['livre', 'date_retour_prevue', 'remarques']
        widgets = {
            'livre': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            # 'date_emprunt': forms.DateInput(attrs={
            #     'class': 'form-control',
            #     'type': 'date'
            # }),
            'date_retour_prevue': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'remarques': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Remarques optionnelles...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer uniquement les livres disponibles
        self.fields['livre'].queryset = Livre.objects.filter(
            nombre_exemplaires_disponibles__gt=0
        )
        
        # Rendre les remarques optionnelles
        self.fields['remarques'].required = False


class SyncEtudiantAPIForm(forms.Form):
    """Formulaire pour synchroniser des étudiants depuis l'API"""
    matricules = forms.CharField(
        label='Matricules des étudiants',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Entrez les matricules (un par ligne)...'
        }),
        help_text='Entrez un matricule par ligne'
    )
    
    def clean_matricules(self):
        matricules = self.cleaned_data.get('matricules', '')
        matricules_list = [m.strip() for m in matricules.split('\n') if m.strip()]
        
        if not matricules_list:
            raise forms.ValidationError("Veuillez entrer au moins un matricule")
        
        if len(matricules_list) > 100:
            raise forms.ValidationError("Maximum 100 matricules à la fois")
        
        return matricules_list


class ImporterEtudiantAPIForm(forms.Form):
    """Formulaire pour importer un étudiant spécifique depuis l'API"""
    type_recherche = forms.ChoiceField(
        label='Type de recherche',
        choices=[
            ('matricule', 'Matricule'),
            ('email', 'Email'),
            ('api_id', 'ID API')
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    valeur_recherche = forms.CharField(
        label='Valeur',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez la valeur de recherche...'
        })
    )
    
    def recuperer_etudiant(self):
        """Récupère l'étudiant depuis l'API"""
        if not self.is_valid():
            return None
        
        type_recherche = self.cleaned_data['type_recherche']
        valeur = self.cleaned_data['valeur_recherche']
        
        try:
            if type_recherche == 'matricule':
                return Etudiant1.recuperer_depuis_api(matricule=valeur)
            elif type_recherche == 'email':
                return Etudiant1.recuperer_depuis_api(email=valeur)
            elif type_recherche == 'api_id':
                return Etudiant1.recuperer_depuis_api(api_id=valeur)
        except Exception as e:
            self.add_error(None, f"Erreur lors de la récupération: {str(e)}")
            return None

     





from django import forms
from .models import Etudiant, Universite, Faculte1, Departement, Classe


class EtudiantForm(forms.ModelForm):
    """
    Formulaire pour l'enregistrement et la modification des étudiants
    """
    
    # Champs obligatoires de base
    matricule = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Matricule de l\'étudiant'
        }),
        label='Matricule'
    )
    
    nom = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom de famille'
        }),
        label='Nom'
    )
    
    prenom = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prénom(s)'
        }),
        label='Prénom'
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'exemple@email.com'
        }),
        label='Email'
    )
    
    telephone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+257 XX XX XX XX'
        }),
        label='Téléphone'
    )
    
    date_naissance = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Date de naissance'
    )
    
    lieu_naissance = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Lieu de naissance'
        }),
        label='Lieu de naissance'
    )
    
    SEXE_CHOICES = [
        ('', '-- Sélectionner --'),
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]
    
    sexe = forms.ChoiceField(
        choices=SEXE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Sexe'
    )
    
    adresse = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Adresse complète'
        }),
        label='Adresse'
    )
    
    # Champs de relations
    universite = forms.ModelChoiceField(
        queryset=Universite.objects.all(),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Université',
        empty_label='-- Sélectionner une université --'
    )
    
    faculte = forms.ModelChoiceField(
        queryset=Faculte1.objects.none(),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Faculté',
        empty_label='-- Sélectionner une faculté --'
    )
    
    departement = forms.ModelChoiceField(
        queryset=Departement.objects.none(),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Département',
        empty_label='-- Sélectionner un département --'
    )
    
    classe = forms.ModelChoiceField(
        queryset=Classe.objects.none(),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Classe',
        empty_label='-- Sélectionner une classe --'
    )
    
    niveau_etude = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: L1, L2, M1, etc.'
        }),
        label='Niveau d\'étude'
    )
    
    annee_academique = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 2024-2025'
        }),
        label='Année académique'
    )
    
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
        ('suspendu', 'Suspendu'),
        ('diplome', 'Diplômé'),
    ]
    
    statut = forms.ChoiceField(
        choices=STATUT_CHOICES,
        initial='actif',
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Statut'
    )
    
    class Meta:
        model = Etudiant
        fields = [
            'matricule', 'nom', 'prenom', 'email', 'telephone',
            'date_naissance', 'lieu_naissance', 'sexe', 'adresse',
            'universite', 'faculte', 'departement', 'classe',
            'niveau_etude', 'annee_academique', 'statut'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si on modifie un étudiant existant
        if self.instance.pk:
            # Charger les facultés de l'université sélectionnée
            if self.instance.universite:
                self.fields['faculte'].queryset = Faculte1.objects.filter(
                    universite=self.instance.universite
                )
            
            # Charger les départements de la faculté sélectionnée
            if self.instance.faculte:
                self.fields['departement'].queryset = Departement.objects.filter(
                    faculte=self.instance.faculte
                )
            
            # Charger les classes du département sélectionné
            if self.instance.departement:
                self.fields['classe'].queryset = Classe.objects.filter(
                    departement=self.instance.departement
                )
        
        # Gérer les données POST pour les selects dépendants
        if 'universite' in self.data:
            try:
                universite_id = int(self.data.get('universite'))
                self.fields['faculte'].queryset = Faculte1.objects.filter(
                    universite_id=universite_id
                ).order_by('nom')
            except (ValueError, TypeError):
                pass
        
        if 'faculte' in self.data:
            try:
                faculte_id = int(self.data.get('faculte'))
                self.fields['departement'].queryset = Departement.objects.filter(
                    faculte_id=faculte_id
                ).order_by('nom')
            except (ValueError, TypeError):
                pass
        
        if 'departement' in self.data:
            try:
                departement_id = int(self.data.get('departement'))
                self.fields['classe'].queryset = Classe.objects.filter(
                    departement_id=departement_id
                ).order_by('nom')
            except (ValueError, TypeError):
                pass
    
    def clean_matricule(self):
        """Valider l'unicité du matricule"""
        matricule = self.cleaned_data.get('matricule')
        
        # Vérifier si un autre étudiant a déjà ce matricule
        qs = Etudiant.objects.filter(matricule=matricule)
        
        # Exclure l'instance actuelle en cas de modification
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise forms.ValidationError(
                'Ce matricule est déjà utilisé par un autre étudiant.'
            )
        
        return matricule
    
    def clean_email(self):
        """Valider l'unicité de l'email"""
        email = self.cleaned_data.get('email')
        
        # Vérifier si un autre étudiant a déjà cet email
        qs = Etudiant.objects.filter(email=email)
        
        # Exclure l'instance actuelle en cas de modification
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise forms.ValidationError(
                'Cet email est déjà utilisé par un autre étudiant.'
            )
        
        return email
    
    def clean(self):
        """Validation globale du formulaire"""
        cleaned_data = super().clean()
        
        # Vérifier la cohérence des relations hiérarchiques
        universite = cleaned_data.get('universite')
        faculte = cleaned_data.get('faculte')
        departement = cleaned_data.get('departement')
        classe = cleaned_data.get('classe')
        
        if faculte and universite:
            if faculte.universite != universite:
                self.add_error('faculte', 
                    'Cette faculté n\'appartient pas à l\'université sélectionnée.')
        
        if departement and faculte:
            if departement.faculte != faculte:
                self.add_error('departement', 
                    'Ce département n\'appartient pas à la faculté sélectionnée.')
        
        if classe and departement:
            if classe.departement != departement:
                self.add_error('classe', 
                    'Cette classe n\'appartient pas au département sélectionné.')
        
        return cleaned_data
    
    
# forms.py - Formulaires pour la hiérarchie académique

from django import forms
from .models import Faculte1, Departement, Classe


class Faculte1Form(forms.ModelForm):
    """
    Formulaire pour créer/modifier une faculté
    """
    nom = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Faculté des Sciences'
        }),
        label='Nom de la faculté'
    )
    
    sigle = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: FS'
        }),
        label='Sigle'
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Description de la faculté...'
        }),
        label='Description'
    )
    
    actif = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Actif'
    )
    
    class Meta:
        model = Faculte1
        fields = ['nom', 'sigle', 'description', 'actif']
    
    def clean_sigle(self):
        """Valider le sigle"""
        sigle = self.cleaned_data.get('sigle')
        if sigle:
            sigle = sigle.upper()
        return sigle


class DepartementForm(forms.ModelForm):
    """
    Formulaire pour créer/modifier un département
    """
    nom = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Département d\'Informatique'
        }),
        label='Nom du département'
    )
    
    sigle = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: INFO'
        }),
        label='Sigle'
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Description du département...'
        }),
        label='Description'
    )
    
    chef_departement = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom du chef de département'
        }),
        label='Chef de département'
    )
    
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@exemple.com'
        }),
        label='Email du département'
    )
    
    telephone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+257 XX XX XX XX'
        }),
        label='Téléphone'
    )
    
    actif = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Actif'
    )
    
    class Meta:
        model = Departement
        fields = ['nom', 'sigle', 'description', 'chef_departement', 'email', 'telephone', 'actif']
    
    def clean_sigle(self):
        """Valider le sigle"""
        sigle = self.cleaned_data.get('sigle')
        if sigle:
            sigle = sigle.upper()
        return sigle


class ClasseForm(forms.ModelForm):
    """
    Formulaire pour créer/modifier une classe
    """
    nom = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Informatique L1'
        }),
        label='Nom de la classe'
    )
    
    code = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: INFO-L1-2025'
        }),
        label='Code de la classe'
    )
    
    NIVEAU_CHOICES = [
        ('', '-- Sélectionner --'),
        ('L1', 'Licence 1'),
        ('L2', 'Licence 2'),
        ('L3', 'Licence 3'),
        ('M1', 'Master 1'),
        ('M2', 'Master 2'),
        ('D1', 'Doctorat 1'),
        ('D2', 'Doctorat 2'),
        ('D3', 'Doctorat 3'),
    ]
    
    niveau = forms.ChoiceField(
        choices=NIVEAU_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Niveau d\'étude'
    )
    
    annee_academique = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 2024-2025'
        }),
        label='Année académique'
    )
    
    capacite_max = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 50',
            'min': 1
        }),
        label='Capacité maximale'
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Description de la classe...'
        }),
        label='Description'
    )
    
    actif = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Active'
    )
    
    class Meta:
        model = Classe
        fields = ['nom', 'code', 'niveau', 'annee_academique', 'capacite_max', 'description', 'actif']
    
    def clean_code(self):
        """Valider le code"""
        code = self.cleaned_data.get('code')
        if code:
            code = code.upper()
        return code
    
    def clean(self):
        """Validation globale"""
        cleaned_data = super().clean()
        capacite_max = cleaned_data.get('capacite_max')
        
        if capacite_max and capacite_max < 1:
            self.add_error('capacite_max', 'La capacité doit être au moins 1.')
        
        return cleaned_data
    
    
    
    from django import forms
from .models import Etudiant1

class InscriptionEtudiantForm(forms.ModelForm):
    """Formulaire d'inscription publique pour les étudiants"""
    
    accepte_conditions = forms.BooleanField(
        required=True,
        label="J'accepte les conditions d'utilisation de la bibliothèque",
        error_messages={
            'required': 'Vous devez accepter les conditions pour continuer'
        }
    )
    
    class Meta:
        model = Etudiant1
        fields = [
            'nom', 'prenom', 'email', 'telephone',
            'date_naissance', 'lieu_naissance', 'sexe', 'adresse',
            'universite', 'faculte', 'departement', 'classe',
            'niveau_etude', 'annee_academique'
        ]
        
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre nom',
                'required': True
            }),
            'prenom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre prénom',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'exemple@email.com',
                'required': True
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+257 XX XX XX XX'
            }),
            'date_naissance': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'lieu_naissance': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ville de naissance'
            }),
            'sexe': forms.Select(attrs={
                'class': 'form-select'
            }),
            'adresse': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Votre adresse complète'
            }),
            'universite': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'faculte': forms.Select(attrs={
                'class': 'form-select'
            }),
            'departement': forms.Select(attrs={
                'class': 'form-select'
            }),
            'classe': forms.Select(attrs={
                'class': 'form-select'
            }),
            'niveau_etude': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: L1, L2, M1, M2'
            }),
            'annee_academique': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 2024-2025'
            }),
        }
        
        labels = {
            'nom': 'Nom',
            'prenom': 'Prénom',
            'email': 'Adresse email',
            'telephone': 'Numéro de téléphone',
            'date_naissance': 'Date de naissance',
            'lieu_naissance': 'Lieu de naissance',
            'sexe': 'Sexe',
            'adresse': 'Adresse complète',
            'universite': 'Université',
            'faculte': 'Faculté',
            'departement': 'Département',
            'classe': 'Classe',
            'niveau_etude': "Niveau d'étude",
            'annee_academique': 'Année académique',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Rendre certains champs obligatoires
        self.fields['nom'].required = True
        self.fields['prenom'].required = True
        self.fields['email'].required = True
        self.fields['universite'].required = True
        
        # Ajouter un choix vide pour les selects
        self.fields['universite'].empty_label = "Sélectionnez une université"
        self.fields['faculte'].empty_label = "Sélectionnez une faculté"
        self.fields['departement'].empty_label = "Sélectionnez un département"
        self.fields['classe'].empty_label = "Sélectionnez une classe"
        self.fields['sexe'].empty_label = "Sélectionnez votre sexe"
    
    def clean_email(self):
        """Vérifier que l'email n'existe pas déjà"""
        email = self.cleaned_data.get('email')
        if email and Etudiant.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Un compte avec cet email existe déjà. '
                'Veuillez utiliser une autre adresse email.'
            )
        return email
    
    def clean_telephone(self):
        """Nettoyer le numéro de téléphone"""
        telephone = self.cleaned_data.get('telephone')
        if telephone:
            # Retirer les espaces et caractères spéciaux
            telephone = ''.join(filter(str.isdigit, telephone))
        return telephone
    
    def save(self, commit=True):
        """Sauvegarder l'étudiant avec le statut inactif"""
        etudiant = super().save(commit=False)
        etudiant.statut = 'inactif'  # En attente de validation
        
        if commit:
            etudiant.save()
        
        return etudiant