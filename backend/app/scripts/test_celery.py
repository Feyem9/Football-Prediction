"""
Script de test pour vérifier la configuration Celery et Redis.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tasks.sync_tasks import sync_daily_matches

def test_celery():
    print("🐇 Test configuration Celery & Redis...")
    try:
        # On tente d'envoyer une tâche
        # Note: Sans worker actif, la tâche restera en 'PENDING' dans Redis
        task = sync_daily_matches.delay()
        print(f"✅ Tâche envoyée avec succès ! ID: {task.id}")
        print("   (La connexion Redis fonctionne a priori)")
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de la tâche : {e}")
        print("   Assurez-vous que le serveur Redis tourne (sudo systemctl start redis-server)")

if __name__ == "__main__":
    test_celery()
