#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script utilitaire pour charger les données depuis JSON et lancer l'analyse APEX-30
"""

import json
import sys
from apex30_pronostic import (
    APEX30Analyzer, EquipeData, MatchData, HistoriqueH2H, 
    CotesMarche, JoueurAbsent, MatchAVenir
)


def charger_match_depuis_json(fichier_json: str):
    """
    Charge les données d'un match depuis un fichier JSON et lance l'analyse
    
    Args:
        fichier_json: Chemin vers le fichier JSON de configuration
    """
    # Charger le JSON
    with open(fichier_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Convertir les matchs historiques en objets MatchData
    def convertir_matchs(matchs_list):
        return [
            MatchData(
                date=m['date'],
                domicile=m['domicile'],
                resultat=m['resultat'],
                buts_pour=m['buts_pour'],
                buts_contre=m['buts_contre'],
                adversaire_classement=m['adversaire_classement'],
                competition=m['competition'],
                xg_pour=m.get('xg_pour', 0.0),
                xg_contre=m.get('xg_contre', 0.0),
                possession=m.get('possession', 0.0),
                tirs_cadres=m.get('tirs_cadres', 0),
                corners_obtenus=m.get('corners_obtenus', 0),
                corners_concedes=m.get('corners_concedes', 0)
            )
            for m in matchs_list
        ]
    
    # Convertir le calendrier
    def convertir_calendrier(cal_list):
        return [
            MatchAVenir(
                date=m['date'],
                competition=m['competition'],
                importance=m['importance'],
                distance_km=m.get('distance_km', 0)
            )
            for m in cal_list
        ]
    
    # Convertir les absences
    def convertir_absences(abs_list):
        return [
            JoueurAbsent(
                nom=j['nom'],
                poste=j['poste'],
                importance=j['importance'],
                depuis_combien_temps=j.get('depuis_combien_temps', 0)
            )
            for j in abs_list
        ]
    
    # Créer l'équipe A
    eq_a_data = data['equipe_a']
    equipe_a = EquipeData(
        nom=eq_a_data['nom'],
        matchs_historique=convertir_matchs(eq_a_data['matchs_historique']),
        classement_actuel=eq_a_data['classement_actuel'],
        points_domicile_saison=eq_a_data['points_domicile_saison'],
        points_exterieur_saison=eq_a_data['points_exterieur_saison'],
        est_domicile=eq_a_data['est_domicile'],
        calendrier_avant=convertir_calendrier(eq_a_data.get('calendrier_avant', [])),
        calendrier_apres=convertir_calendrier(eq_a_data.get('calendrier_apres', [])),
        joueurs_absents=convertir_absences(eq_a_data.get('joueurs_absents', [])),
        points_du_leader=eq_a_data.get('points_du_leader', 0),
        situation=eq_a_data.get('situation', 'Milieu de tableau'),
        serie_actuelle=eq_a_data.get('serie_actuelle', ''),
        entraîneur_nouveau=eq_a_data.get('entraineur_nouveau', False),
        entraîneur_sous_pression=eq_a_data.get('entraineur_sous_pression', False),
        derby=eq_a_data.get('derby', False)
    )
    
    # Créer l'équipe B
    eq_b_data = data['equipe_b']
    equipe_b = EquipeData(
        nom=eq_b_data['nom'],
        matchs_historique=convertir_matchs(eq_b_data['matchs_historique']),
        classement_actuel=eq_b_data['classement_actuel'],
        points_domicile_saison=eq_b_data['points_domicile_saison'],
        points_exterieur_saison=eq_b_data['points_exterieur_saison'],
        est_domicile=eq_b_data['est_domicile'],
        calendrier_avant=convertir_calendrier(eq_b_data.get('calendrier_avant', [])),
        calendrier_apres=convertir_calendrier(eq_b_data.get('calendrier_apres', [])),
        joueurs_absents=convertir_absences(eq_b_data.get('joueurs_absents', [])),
        points_du_leader=eq_b_data.get('points_du_leader', 0),
        situation=eq_b_data.get('situation', 'Milieu de tableau'),
        serie_actuelle=eq_b_data.get('serie_actuelle', ''),
        entraîneur_nouveau=eq_b_data.get('entraineur_nouveau', False),
        entraîneur_sous_pression=eq_b_data.get('entraineur_sous_pression', False),
        derby=eq_b_data.get('derby', False)
    )
    
    # Créer l'historique H2H
    h2h_data = data['historique_h2h']
    h2h = HistoriqueH2H(
        victoires_equipe_a=h2h_data['victoires_equipe_a'],
        nuls=h2h_data['nuls'],
        victoires_equipe_b=h2h_data['victoires_equipe_b'],
        matchs_serres=h2h_data['matchs_serres'],
        derniers_gagnants=h2h_data['derniers_gagnants']
    )
    
    # Créer les cotes (optionnel)
    cotes = None
    if 'cotes' in data:
        cotes_data = data['cotes']
        cotes = CotesMarche(
            victoire_equipe_a=cotes_data['victoire_equipe_a'],
            nul=cotes_data['nul'],
            victoire_equipe_b=cotes_data['victoire_equipe_b'],
            cote_initiale_equipe_a=cotes_data.get('cote_initiale_equipe_a', 0.0),
            cote_initiale_equipe_b=cotes_data.get('cote_initiale_equipe_b', 0.0)
        )
    
    # Lancer l'analyse
    print(f"\n{'='*80}")
    print(f"CHARGEMENT DU FICHIER: {fichier_json}")
    print(f"{'='*80}\n")
    
    analyzer = APEX30Analyzer()
    resultat = analyzer.analyser_match(equipe_a, equipe_b, h2h, cotes)
    
    # Sauvegarder le rapport
    nom_rapport = fichier_json.replace('.json', '_rapport.txt')
    with open(nom_rapport, 'w', encoding='utf-8') as f:
        f.write(resultat['rapport'])
    
    print(f"\n✅ Rapport complet sauvegardé dans: {nom_rapport}")
    
    # Sauvegarder le résultat JSON
    nom_json_result = fichier_json.replace('.json', '_resultat.json')
    with open(nom_json_result, 'w', encoding='utf-8') as f:
        json.dump({
            'equipe_a': {
                'nom': resultat['equipe_a']['nom'],
                'score_total': round(resultat['equipe_a']['score_total'], 2),
                'scores_detailles': {k: round(v, 2) for k, v in resultat['equipe_a']['scores'].items()}
            },
            'equipe_b': {
                'nom': resultat['equipe_b']['nom'],
                'score_total': round(resultat['equipe_b']['score_total'], 2),
                'scores_detailles': {k: round(v, 2) for k, v in resultat['equipe_b']['scores'].items()}
            },
            'decision': resultat['decision']
        }, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Résultat JSON sauvegardé dans: {nom_json_result}")
    
    return resultat


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python charger_json.py <fichier_config.json>")
        print("\nExemple: python charger_json.py config_exemple.json")
        sys.exit(1)
    
    fichier = sys.argv[1]
    
    try:
        resultat = charger_match_depuis_json(fichier)
        print("\n✅ Analyse terminée avec succès!")
    except FileNotFoundError:
        print(f"❌ Erreur: Le fichier '{fichier}' n'existe pas")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Erreur: Le fichier JSON est invalide - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
