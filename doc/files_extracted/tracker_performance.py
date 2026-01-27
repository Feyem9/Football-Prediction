#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tracker de Performance APEX-30
Permet de suivre vos analyses et paris pour améliorer le système
"""

import json
import os
from datetime import datetime
from typing import List, Dict


class PerformanceTracker:
    """Suivi des performances et statistiques"""
    
    def __init__(self, fichier_historique='historique_paris.json'):
        self.fichier = fichier_historique
        self.historique = self._charger_historique()
    
    def _charger_historique(self) -> List[Dict]:
        """Charge l'historique des paris"""
        if os.path.exists(self.fichier):
            with open(self.fichier, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _sauvegarder_historique(self):
        """Sauvegarde l'historique"""
        with open(self.fichier, 'w', encoding='utf-8') as f:
            json.dump(self.historique, f, indent=2, ensure_ascii=False)
    
    def ajouter_pari(self, 
                     date: str,
                     equipe_a: str,
                     equipe_b: str,
                     score_a: float,
                     score_b: float,
                     pronostic: str,
                     cote: float,
                     mise_unites: float,
                     confiance: str,
                     value_bet: bool = False):
        """
        Enregistre un nouveau pari
        """
        pari = {
            'id': len(self.historique) + 1,
            'date': date,
            'match': f"{equipe_a} vs {equipe_b}",
            'equipe_a': equipe_a,
            'equipe_b': equipe_b,
            'score_analyse_a': score_a,
            'score_analyse_b': score_b,
            'ecart': abs(score_a - score_b),
            'pronostic': pronostic,
            'cote': cote,
            'mise_unites': mise_unites,
            'confiance': confiance,
            'value_bet': value_bet,
            'resultat_reel': None,  # À remplir après le match
            'gain_perte': None,
            'statut': 'En attente'
        }
        
        self.historique.append(pari)
        self._sauvegarder_historique()
        
        print(f"✅ Pari #{pari['id']} enregistré: {pari['match']}")
        print(f"   Pronostic: {pronostic} @ {cote}")
        print(f"   Mise: {mise_unites} unités")
    
    def mettre_a_jour_resultat(self, pari_id: int, resultat: str):
        """
        Met à jour le résultat d'un pari
        
        Args:
            pari_id: ID du pari
            resultat: 'V' (victoire), 'N' (nul), 'D' (défaite)
        """
        for pari in self.historique:
            if pari['id'] == pari_id:
                pari['resultat_reel'] = resultat
                
                # Calculer gain/perte
                pronostic_correct = self._verifier_pronostic(pari['pronostic'], resultat)
                
                if pronostic_correct:
                    pari['gain_perte'] = pari['mise_unites'] * (pari['cote'] - 1)
                    pari['statut'] = 'Gagné'
                else:
                    pari['gain_perte'] = -pari['mise_unites']
                    pari['statut'] = 'Perdu'
                
                self._sauvegarder_historique()
                
                symbole = "✅" if pronostic_correct else "❌"
                print(f"{symbole} Pari #{pari_id} mis à jour: {pari['statut']}")
                print(f"   Gain/Perte: {pari['gain_perte']:+.2f} unités")
                return
        
        print(f"❌ Pari #{pari_id} introuvable")
    
    def _verifier_pronostic(self, pronostic: str, resultat: str) -> bool:
        """Vérifie si le pronostic était correct"""
        pronostic_lower = pronostic.lower()
        
        # Victoire équipe A
        if 'victoire' in pronostic_lower and 'équipe a' in pronostic_lower:
            return resultat == 'V_A'
        
        # Victoire équipe B
        if 'victoire' in pronostic_lower and 'équipe b' in pronostic_lower:
            return resultat == 'V_B'
        
        # Match nul
        if 'nul' in pronostic_lower:
            return resultat == 'N'
        
        # Double chance (à affiner selon le pronostic exact)
        if 'double chance' in pronostic_lower:
            return resultat != 'D'  # Simplification
        
        return False
    
    def statistiques(self) -> Dict:
        """Calcule les statistiques globales"""
        total = len(self.historique)
        en_attente = sum(1 for p in self.historique if p['statut'] == 'En attente')
        termines = total - en_attente
        
        if termines == 0:
            print("Aucun pari terminé pour le moment")
            return {}
        
        gagnes = sum(1 for p in self.historique if p['statut'] == 'Gagné')
        perdus = sum(1 for p in self.historique if p['statut'] == 'Perdu')
        
        taux_reussite = (gagnes / termines * 100) if termines > 0 else 0
        
        total_mise = sum(p['mise_unites'] for p in self.historique if p['statut'] != 'En attente')
        total_gain_perte = sum(p['gain_perte'] for p in self.historique if p['gain_perte'] is not None)
        
        roi = (total_gain_perte / total_mise * 100) if total_mise > 0 else 0
        
        stats = {
            'total_paris': total,
            'en_attente': en_attente,
            'termines': termines,
            'gagnes': gagnes,
            'perdus': perdus,
            'taux_reussite': taux_reussite,
            'total_mise': total_mise,
            'total_gain_perte': total_gain_perte,
            'roi': roi
        }
        
        # Stats par niveau de confiance
        stats_confiance = {}
        for niveau in ['Forte confiance', 'Confiance modérée', 'Match serré']:
            paris_niveau = [p for p in self.historique 
                           if p['confiance'] == niveau and p['statut'] != 'En attente']
            if paris_niveau:
                gagnes_niveau = sum(1 for p in paris_niveau if p['statut'] == 'Gagné')
                stats_confiance[niveau] = {
                    'total': len(paris_niveau),
                    'gagnes': gagnes_niveau,
                    'taux': gagnes_niveau / len(paris_niveau) * 100
                }
        
        stats['par_confiance'] = stats_confiance
        
        # Stats value bets
        value_bets = [p for p in self.historique if p['value_bet'] and p['statut'] != 'En attente']
        if value_bets:
            gagnes_vb = sum(1 for p in value_bets if p['statut'] == 'Gagné')
            stats['value_bets'] = {
                'total': len(value_bets),
                'gagnes': gagnes_vb,
                'taux': gagnes_vb / len(value_bets) * 100
            }
        
        return stats
    
    def afficher_statistiques(self):
        """Affiche les statistiques de manière formatée"""
        stats = self.statistiques()
        
        if not stats:
            return
        
        print("\n" + "="*80)
        print("📊 STATISTIQUES DE PERFORMANCE APEX-30")
        print("="*80)
        
        print(f"\n📈 BILAN GLOBAL")
        print(f"   Total de paris: {stats['total_paris']}")
        print(f"   En attente: {stats['en_attente']}")
        print(f"   Terminés: {stats['termines']}")
        print(f"   Gagnés: {stats['gagnes']} ✅")
        print(f"   Perdus: {stats['perdus']} ❌")
        print(f"   Taux de réussite: {stats['taux_reussite']:.1f}%")
        
        print(f"\n💰 RENTABILITÉ")
        print(f"   Total misé: {stats['total_mise']:.2f} unités")
        print(f"   Gain/Perte: {stats['total_gain_perte']:+.2f} unités")
        print(f"   ROI: {stats['roi']:+.1f}%")
        
        if stats['roi'] > 10:
            print(f"   🎉 Excellent ROI!")
        elif stats['roi'] > 0:
            print(f"   👍 ROI positif, continuez!")
        else:
            print(f"   ⚠️  ROI négatif, analysez vos erreurs")
        
        if 'par_confiance' in stats and stats['par_confiance']:
            print(f"\n📊 PAR NIVEAU DE CONFIANCE")
            for niveau, data in stats['par_confiance'].items():
                print(f"   {niveau}:")
                print(f"      Total: {data['total']} | Taux: {data['taux']:.1f}%")
        
        if 'value_bets' in stats:
            print(f"\n💎 VALUE BETS")
            print(f"   Total: {stats['value_bets']['total']}")
            print(f"   Taux de réussite: {stats['value_bets']['taux']:.1f}%")
        
        print("\n" + "="*80)
    
    def meilleurs_pires_paris(self, n=5):
        """Affiche les meilleurs et pires paris"""
        termines = [p for p in self.historique if p['statut'] != 'En attente']
        
        if not termines:
            print("Aucun pari terminé")
            return
        
        termines_tries = sorted(termines, key=lambda x: x['gain_perte'], reverse=True)
        
        print("\n" + "="*80)
        print(f"🏆 TOP {n} MEILLEURS PARIS")
        print("="*80)
        
        for i, pari in enumerate(termines_tries[:n], 1):
            print(f"{i}. {pari['match']} ({pari['date']})")
            print(f"   Pronostic: {pari['pronostic']} @ {pari['cote']}")
            print(f"   Gain: +{pari['gain_perte']:.2f} unités ✅")
            print()
        
        print("="*80)
        print(f"💸 TOP {n} PIRES PARIS")
        print("="*80)
        
        for i, pari in enumerate(reversed(termines_tries[-n:]), 1):
            print(f"{i}. {pari['match']} ({pari['date']})")
            print(f"   Pronostic: {pari['pronostic']} @ {pari['cote']}")
            print(f"   Perte: {pari['gain_perte']:.2f} unités ❌")
            print()
    
    def conseils_amelioration(self):
        """Fournit des conseils basés sur les performances"""
        stats = self.statistiques()
        
        if not stats or stats['termines'] < 10:
            print("\n⚠️  Pas assez de données (minimum 10 paris terminés)")
            return
        
        print("\n" + "="*80)
        print("💡 CONSEILS D'AMÉLIORATION")
        print("="*80)
        
        # Analyse du taux de réussite
        if stats['taux_reussite'] < 55:
            print("\n❌ Taux de réussite faible (<55%)")
            print("   → Soyez PLUS sélectif")
            print("   → Augmentez le seuil minimum de confiance")
            print("   → Spécialisez-vous sur moins de championnats")
        
        elif stats['taux_reussite'] > 70:
            print("\n✅ Excellent taux de réussite!")
            print("   → Vous pouvez peut-être augmenter légèrement vos mises")
            print("   → Continuez votre approche actuelle")
        
        # Analyse du ROI
        if stats['roi'] < 0:
            print("\n❌ ROI négatif")
            print("   → Réduisez IMMÉDIATEMENT vos mises")
            print("   → Analysez vos erreurs récurrentes")
            print("   → Envisagez une pause pour réévaluer votre stratégie")
        
        elif stats['roi'] < 5:
            print("\n⚠️  ROI faiblement positif")
            print("   → Attention à la variance")
            print("   → Maintenez votre discipline")
        
        # Analyse par confiance
        if 'par_confiance' in stats:
            for niveau, data in stats['par_confiance'].items():
                if data['taux'] < 50 and data['total'] >= 5:
                    print(f"\n⚠️  Mauvais résultats en '{niveau}'")
                    print(f"   → Évitez ce niveau de confiance temporairement")
        
        # Conseils value bets
        if 'value_bets' in stats:
            if stats['value_bets']['taux'] > stats['taux_reussite']:
                print("\n✅ Vos value bets performent bien!")
                print("   → Continuez à les prioriser")
            else:
                print("\n⚠️  Vos value bets sous-performent")
                print("   → Revoyez votre méthode de détection")
        
        print("\n" + "="*80)


def exemple_utilisation_tracker():
    """Exemple d'utilisation du tracker"""
    
    tracker = PerformanceTracker()
    
    print("\n=== EXEMPLE D'UTILISATION DU TRACKER ===\n")
    
    # Ajouter quelques paris exemples
    tracker.ajouter_pari(
        date="2025-01-20",
        equipe_a="PSG",
        equipe_b="Lyon",
        score_a=2.89,
        score_b=2.19,
        pronostic="Victoire PSG",
        cote=1.65,
        mise_unites=3,
        confiance="Confiance modérée",
        value_bet=False
    )
    
    # Simuler quelques résultats
    if len(tracker.historique) >= 1:
        tracker.mettre_a_jour_resultat(1, 'V_A')  # PSG a gagné
    
    # Afficher les statistiques
    tracker.afficher_statistiques()


if __name__ == "__main__":
    exemple_utilisation_tracker()
