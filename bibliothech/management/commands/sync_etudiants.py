from django.core.management.base import BaseCommand
from bibliothech.models import Etudiant1
import csv


class Command(BaseCommand):
    help = 'Synchronise les étudiants depuis l\'API'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--fichier',
            type=str,
            help='Fichier CSV contenant les matricules'
        )
        parser.add_argument(
            '--matricule',
            type=str,
            help='Matricule unique à synchroniser'
        )
    
    def handle(self, *args, **options):
        if options['matricule']:
            self.sync_etudiant(options['matricule'])
        elif options['fichier']:
            self.sync_depuis_fichier(options['fichier'])
        else:
            self.stdout.write(
                self.style.ERROR('Veuillez spécifier --matricule ou --fichier')
            )
    
    def sync_etudiant(self, matricule):
        try:
            etudiant = Etudiant1.recuperer_depuis_api(matricule=matricule)
            if etudiant:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Étudiant {etudiant.nom_complet} synchronisé avec succès'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Étudiant {matricule} non trouvé')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erreur pour {matricule}: {str(e)}')
            )
    
    def sync_depuis_fichier(self, fichier):
        succes = 0
        erreurs = 0
        
        with open(fichier, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    matricule = row[0].strip()
                    try:
                        etudiant = Etudiant1.recuperer_depuis_api(matricule=matricule)
                        if etudiant:
                            succes += 1
                        else:
                            erreurs += 1
                    except Exception:
                        erreurs += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Synchronisation terminée: {succes} succès, {erreurs} erreurs'
            )
        )