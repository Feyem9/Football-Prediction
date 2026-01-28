
import os
import sys
from datetime import datetime, timedelta

# Ajouter le chemin de l'app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend/app')))

from services.apex30_service import APEX30Service, EquipeAnalyse, MatchHistorique, H2HStats

def test_apex():
    # Créer le service (Sans DB pour le test)
    apex = APEX30Service(None)
    
    # Créer des données de test
    matchs_a = [
        MatchHistorique(datetime.now() - timedelta(days=i*7), True, 'V', 2, 0, 10, 'Championnat')
        for i in range(5)
    ]
    equipe_a = EquipeAnalyse("Team A", matchs_a, 1, 2.5, 1.5, True, "Titre")
    
    matchs_b = [
        MatchHistorique(datetime.now() - timedelta(days=i*7), False, 'D', 0, 2, 5, 'Championnat')
        for i in range(5)
    ]
    equipe_b = EquipeAnalyse("Team B", matchs_b, 18, 1.0, 0.5, False, "Maintien")
    
    h2h = H2HStats(3, 1, 1, ['A', 'A', 'N'])
    
    print("Test de l'analyse APEX-30...")
    try:
        result = apex.analyser_match(equipe_a, equipe_b, h2h)
        print("✅ Analyse réussie !")
        print(f"Decision: {result['decision']['pronostic']}")
        print(f"Confiance: {result['decision']['confiance_pct']}")
        print("Scores équipe A:", result['equipe_a']['scores'])
    except Exception as e:
        print(f"❌ Échec de l'analyse: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_apex()
