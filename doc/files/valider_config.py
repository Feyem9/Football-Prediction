#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validateur de Configuration APEX-30
Vérifie que votre fichier JSON est correctement formaté avant l'analyse
"""

import json
import sys
from typing import List, Dict, Tuple


class ValidationError(Exception):
    """Erreur de validation"""
    pass


class ConfigValidator:
    """Validateur de fichier de configuration"""
    
    def __init__(self):
        self.erreurs = []
        self.avertissements = []
    
    def valider_fichier(self, fichier_json: str) -> Tuple[bool, List[str], List[str]]:
        """
        Valide un fichier de configuration
        
        Returns:
            (est_valide, liste_erreurs, liste_avertissements)
        """
        self.erreurs = []
        self.avertissements = []
        
        # 1. Charger le JSON
        try:
            with open(fichier_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.erreurs.append(f"Fichier '{fichier_json}' introuvable")
            return False, self.erreurs, self.avertissements
        except json.JSONDecodeError as e:
            self.erreurs.append(f"JSON invalide: {e}")
            return False, self.erreurs, self.avertissements
        
        # 2. Valider la structure
        self._valider_structure(data)
        
        # 3. Valider équipe A
        if 'equipe_a' in data:
            self._valider_equipe(data['equipe_a'], 'Équipe A')
        
        # 4. Valider équipe B
        if 'equipe_b' in data:
            self._valider_equipe(data['equipe_b'], 'Équipe B')
        
        # 5. Valider H2H
        if 'historique_h2h' in data:
            self._valider_h2h(data['historique_h2h'])
        
        # 6. Valider cotes
        if 'cotes' in data:
            self._valider_cotes(data['cotes'])
        
        est_valide = len(self.erreurs) == 0
        
        return est_valide, self.erreurs, self.avertissements
    
    def _valider_structure(self, data: Dict):
        """Valide la structure de base"""
        champs_requis = ['equipe_a', 'equipe_b', 'historique_h2h']
        
        for champ in champs_requis:
            if champ not in data:
                self.erreurs.append(f"Champ requis manquant: '{champ}'")
        
        if 'cotes' not in data:
            self.avertissements.append("Pas de cotes fournies - l'analyse de marché sera ignorée")
    
    def _valider_equipe(self, equipe: Dict, nom_equipe: str):
        """Valide les données d'une équipe"""
        
        # Champs requis
        champs_requis = [
            'nom', 'matchs_historique', 'classement_actuel',
            'points_domicile_saison', 'points_exterieur_saison', 'est_domicile'
        ]
        
        for champ in champs_requis:
            if champ not in equipe:
                self.erreurs.append(f"{nom_equipe}: Champ requis manquant: '{champ}'")
        
        # Valider le nom
        if 'nom' in equipe and not equipe['nom']:
            self.erreurs.append(f"{nom_equipe}: Le nom ne peut pas être vide")
        
        # Valider matchs historique
        if 'matchs_historique' in equipe:
            matchs = equipe['matchs_historique']
            
            if not isinstance(matchs, list):
                self.erreurs.append(f"{nom_equipe}: 'matchs_historique' doit être une liste")
            elif len(matchs) < 5:
                self.erreurs.append(f"{nom_equipe}: Minimum 5 matchs requis (10 recommandés)")
            elif len(matchs) < 10:
                self.avertissements.append(f"{nom_equipe}: Moins de 10 matchs - précision réduite")
            
            # Valider chaque match
            for i, match in enumerate(matchs, 1):
                self._valider_match(match, f"{nom_equipe} - Match {i}")
        
        # Valider classement
        if 'classement_actuel' in equipe:
            if not isinstance(equipe['classement_actuel'], int) or equipe['classement_actuel'] < 1:
                self.erreurs.append(f"{nom_equipe}: Classement invalide (doit être >= 1)")
        
        # Valider points
        for champ in ['points_domicile_saison', 'points_exterieur_saison']:
            if champ in equipe:
                val = equipe[champ]
                if not isinstance(val, (int, float)) or val < 0 or val > 3:
                    self.erreurs.append(f"{nom_equipe}: {champ} invalide (doit être entre 0 et 3)")
        
        # Valider situation
        if 'situation' in equipe:
            situations_valides = ['Titre', 'Europe', 'Maintien', 'Milieu de tableau', 'Relégué', 'Champion']
            if equipe['situation'] not in situations_valides:
                self.avertissements.append(
                    f"{nom_equipe}: Situation '{equipe['situation']}' non standard. "
                    f"Valeurs recommandées: {', '.join(situations_valides)}"
                )
        
        # Valider joueurs absents
        if 'joueurs_absents' in equipe and equipe['joueurs_absents']:
            for i, joueur in enumerate(equipe['joueurs_absents'], 1):
                self._valider_joueur_absent(joueur, f"{nom_equipe} - Joueur {i}")
    
    def _valider_match(self, match: Dict, contexte: str):
        """Valide les données d'un match"""
        champs_requis = [
            'date', 'domicile', 'resultat', 'buts_pour', 
            'buts_contre', 'adversaire_classement', 'competition'
        ]
        
        for champ in champs_requis:
            if champ not in match:
                self.erreurs.append(f"{contexte}: Champ manquant: '{champ}'")
        
        # Valider résultat
        if 'resultat' in match:
            if match['resultat'] not in ['V', 'N', 'D']:
                self.erreurs.append(f"{contexte}: Résultat invalide (doit être V, N ou D)")
        
        # Valider buts
        for champ in ['buts_pour', 'buts_contre']:
            if champ in match:
                if not isinstance(match[champ], int) or match[champ] < 0:
                    self.erreurs.append(f"{contexte}: {champ} invalide (doit être >= 0)")
        
        # Valider adversaire
        if 'adversaire_classement' in match:
            if not isinstance(match['adversaire_classement'], int) or match['adversaire_classement'] < 1:
                self.erreurs.append(f"{contexte}: Classement adversaire invalide (>= 1)")
        
        # Valider compétition
        if 'competition' in match:
            comps_valides = ['Championnat', 'Coupe nationale', 'Coupe d\'Europe']
            if match['competition'] not in comps_valides:
                self.avertissements.append(
                    f"{contexte}: Compétition '{match['competition']}' non standard"
                )
        
        # Vérifier xG
        if 'xg_pour' not in match or match['xg_pour'] == 0:
            self.avertissements.append(f"{contexte}: Pas de xG fourni - précision réduite")
    
    def _valider_joueur_absent(self, joueur: Dict, contexte: str):
        """Valide un joueur absent"""
        champs_requis = ['nom', 'poste', 'importance']
        
        for champ in champs_requis:
            if champ not in joueur:
                self.erreurs.append(f"{contexte}: Champ manquant: '{champ}'")
        
        # Valider poste
        if 'poste' in joueur:
            postes_valides = ['Gardien', 'Defenseur', 'Milieu', 'Attaquant']
            if joueur['poste'] not in postes_valides:
                self.erreurs.append(
                    f"{contexte}: Poste invalide. Valeurs: {', '.join(postes_valides)}"
                )
        
        # Valider importance
        if 'importance' in joueur:
            if not isinstance(joueur['importance'], int) or not (0 <= joueur['importance'] <= 10):
                self.erreurs.append(f"{contexte}: Importance doit être entre 0 et 10")
    
    def _valider_h2h(self, h2h: Dict):
        """Valide l'historique H2H"""
        champs_requis = [
            'victoires_equipe_a', 'nuls', 'victoires_equipe_b',
            'matchs_serres', 'derniers_gagnants'
        ]
        
        for champ in champs_requis:
            if champ not in h2h:
                self.erreurs.append(f"H2H: Champ manquant: '{champ}'")
        
        # Valider cohérence
        if all(c in h2h for c in ['victoires_equipe_a', 'nuls', 'victoires_equipe_b']):
            total = h2h['victoires_equipe_a'] + h2h['nuls'] + h2h['victoires_equipe_b']
            if total == 0:
                self.erreurs.append("H2H: Aucun match historique renseigné")
            elif total < 3:
                self.avertissements.append("H2H: Moins de 3 matchs - données limitées")
        
        # Valider derniers gagnants
        if 'derniers_gagnants' in h2h:
            if not isinstance(h2h['derniers_gagnants'], list):
                self.erreurs.append("H2H: 'derniers_gagnants' doit être une liste")
            else:
                for i, gagnant in enumerate(h2h['derniers_gagnants'], 1):
                    if gagnant not in ['A', 'N', 'B']:
                        self.erreurs.append(
                            f"H2H: Gagnant #{i} invalide (doit être 'A', 'N' ou 'B')"
                        )
    
    def _valider_cotes(self, cotes: Dict):
        """Valide les cotes"""
        champs_requis = ['victoire_equipe_a', 'nul', 'victoire_equipe_b']
        
        for champ in champs_requis:
            if champ not in cotes:
                self.erreurs.append(f"Cotes: Champ manquant: '{champ}'")
            elif cotes[champ] <= 1.0:
                self.erreurs.append(f"Cotes: {champ} invalide (doit être > 1.0)")
        
        # Vérifier cohérence des cotes
        if all(c in cotes for c in champs_requis):
            prob_totale = (1/cotes['victoire_equipe_a'] + 
                          1/cotes['nul'] + 
                          1/cotes['victoire_equipe_b'])
            
            if prob_totale < 0.95 or prob_totale > 1.20:
                self.avertissements.append(
                    f"Cotes: Probabilité totale suspecte ({prob_totale:.2%})"
                )


def valider_et_afficher(fichier_json: str):
    """Valide un fichier et affiche les résultats"""
    
    print(f"\n{'='*80}")
    print(f"VALIDATION DU FICHIER: {fichier_json}")
    print(f"{'='*80}\n")
    
    validator = ConfigValidator()
    est_valide, erreurs, avertissements = validator.valider_fichier(fichier_json)
    
    # Afficher les erreurs
    if erreurs:
        print(f"❌ ERREURS CRITIQUES ({len(erreurs)}):")
        for i, erreur in enumerate(erreurs, 1):
            print(f"   {i}. {erreur}")
        print()
    
    # Afficher les avertissements
    if avertissements:
        print(f"⚠️  AVERTISSEMENTS ({len(avertissements)}):")
        for i, avert in enumerate(avertissements, 1):
            print(f"   {i}. {avert}")
        print()
    
    # Conclusion
    if est_valide:
        if avertissements:
            print("✅ Fichier VALIDE (avec avertissements)")
            print("   Le fichier peut être utilisé, mais certaines données manquent")
            print("   pour une analyse optimale.")
        else:
            print("✅ Fichier PARFAITEMENT VALIDE!")
            print("   Toutes les données sont présentes et correctes.")
    else:
        print("❌ Fichier INVALIDE")
        print(f"   Corrigez les {len(erreurs)} erreur(s) avant de lancer l'analyse.")
    
    print(f"\n{'='*80}\n")
    
    return est_valide


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python valider_config.py <fichier_config.json>")
        print("\nExemple: python valider_config.py config_exemple.json")
        sys.exit(1)
    
    fichier = sys.argv[1]
    
    try:
        est_valide = valider_et_afficher(fichier)
        sys.exit(0 if est_valide else 1)
    except Exception as e:
        print(f"❌ Erreur lors de la validation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
