import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bibliotheque.settings')
django.setup()

from django.core.mail import send_mail

# Test d'envoi d'email
try:
    send_mail(
        'Test Email',
        'Ceci est un email de test depuis Django.',
        'wallaruk12@gmail.com',
        ['niyurukundowilly@gmail.com'],
        fail_silently=False,
    )
    print("✅ Email envoyé avec succès !")
except Exception as e:
    print(f"❌ Erreur lors de l'envoi : {e}")