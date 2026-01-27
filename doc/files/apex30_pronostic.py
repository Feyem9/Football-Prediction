#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEX-30 - Système Professionnel de Pronostic Sportif
30 ans d'expérience condensés en code

Auteur: Système Expert
Version: 1.0
"""

import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


class FormLevel(Enum):
    """Niveaux de forme d'une équipe"""
    CRITIQUE = "Critique"
    FAIBLE = "Faible"
    MOYENNE = "Moyenne"
    BONNE = "Bonne"
    EXCELLENTE = "Excellente"


class ConfidenceLevel(Enum):
    """Niveaux de confiance du pronostic"""
    INCERTITUDE = "Incertitude - NE PAS PARIER"
    MATCH_SERRE = "Match serré"
    CONFIANCE_MODEREE = "Confiance modérée"
    FORTE_CONFIANCE = "Forte confiance"


@dataclass
class MatchData:
    """Données d'un match historique"""
    date: str
    domicile: bool
    resultat: str  # 'V', 'N', 'D'
    buts_pour: int
    buts_contre: int
    adversaire_classement: int  # Position au classement (1-20)
    competition: str  # 'Championnat', 'Coupe'
    xg_pour: float = 0.0
    xg_contre: float = 0.0
    possession: float = 0.0
    tirs_cadres: int = 0
    corners_obtenus: int = 0
    corners_concedes: int = 0


@dataclass
class JoueurAbsent:
    """Joueur absent ou blessé"""
    nom: str
    poste: str  # 'Gardien', 'Defenseur', 'Milieu', 'Attaquant'
    importance: int  # 0-10
    depuis_combien_temps: int  # jours


@dataclass
class MatchAVenir:
    """Match à venir dans le calendrier"""
    date: str
    competition: str
    importance: str  # 'Normal', 'Important', 'Crucial'
    distance_km: int = 0


@dataclass
class EquipeData:
    """Données complètes d'une équipe"""
    nom: str
    matchs_historique: List[MatchData]
    classement_actuel: int
    points_domicile_saison: float  # Points moyens par match à domicile
    points_exterieur_saison: float  # Points moyens par match à l'extérieur
    est_domicile: bool  # Pour le match à analyser
    
    # Contexte
    calendrier_avant: List[MatchAVenir] = field(default_factory=list)
    calendrier_apres: List[MatchAVenir] = field(default_factory=list)
    joueurs_absents: List[JoueurAbsent] = field(default_factory=list)
    
    # Situation
    points_du_leader: int = 0  # Écart avec le leader (négatif si leader)
    situation: str = "Milieu de tableau"  # 'Titre', 'Europe', 'Maintien', 'Relégué', etc.
    serie_actuelle: str = ""  # "3V", "2D1N", etc.
    entraîneur_nouveau: bool = False
    entraîneur_sous_pression: bool = False
    derby: bool = False


@dataclass
class HistoriqueH2H:
    """Historique des confrontations directes"""
    victoires_equipe_a: int
    nuls: int
    victoires_equipe_b: int
    matchs_serres: int  # Matchs avec 1 but d'écart ou nuls
    derniers_gagnants: List[str]  # Liste des 5 derniers gagnants ['A', 'B', 'N']


@dataclass
class CotesMarche:
    """Cotes du marché"""
    victoire_equipe_a: float
    nul: float
    victoire_equipe_b: float
    cote_initiale_equipe_a: float = 0.0  # Pour détecter les mouvements
    cote_initiale_equipe_b: float = 0.0


class APEX30Analyzer:
    """
    Analyseur principal du système APEX-30
    """
    
    # Coefficients de pondération pour le score final
    POIDS = {
        'ifp': 0.25,
        'force_offensive': 0.15,
        'solidite_defensive': 0.15,
        'facteur_domicile': 0.10,
        'fatigue': 0.05,
        'motivation': 0.15,
        'absences': 0.10,
        'h2h': 0.05
    }
    
    def __init__(self):
        """Initialisation de l'analyseur"""
        self.rapport = []
    
    def analyser_match(self, 
                      equipe_a: EquipeData, 
                      equipe_b: EquipeData,
                      h2h: HistoriqueH2H,
                      cotes: Optional[CotesMarche] = None) -> Dict:
        """
        Analyse complète d'un match
        
        Returns:
            Dictionnaire avec le pronostic complet et tous les scores
        """
        self.rapport = []
        self._log(f"\n{'='*80}")
        self._log(f"ANALYSE APEX-30: {equipe_a.nom} vs {equipe_b.nom}")
        self._log(f"{'='*80}\n")
        
        # Phase 1: Calcul des modules pour équipe A
        self._log(f"\n--- ANALYSE DE {equipe_a.nom.upper()} ---")
        scores_a = self._analyser_equipe(equipe_a)
        
        # Phase 2: Calcul des modules pour équipe B
        self._log(f"\n--- ANALYSE DE {equipe_b.nom.upper()} ---")
        scores_b = self._analyser_equipe(equipe_b)
        
        # Phase 3: Historique H2H
        self._log(f"\n--- HISTORIQUE DES CONFRONTATIONS ---")
        h2h_scores = self._analyser_h2h(h2h, equipe_a.nom, equipe_b.nom)
        scores_a['h2h'] = h2h_scores['equipe_a']
        scores_b['h2h'] = h2h_scores['equipe_b']
        
        # Phase 4: Calcul des scores totaux
        score_total_a = self._calculer_score_total(scores_a)
        score_total_b = self._calculer_score_total(scores_b)
        
        # Phase 5: Analyse du marché (si disponible)
        value_bet = None
        if cotes:
            self._log(f"\n--- ANALYSE DU MARCHÉ ---")
            value_bet = self._analyser_marche(cotes, score_total_a, score_total_b)
        
        # Phase 6: Décision finale
        self._log(f"\n{'='*80}")
        self._log(f"SYNTHÈSE FINALE")
        self._log(f"{'='*80}")
        decision = self._generer_decision(
            equipe_a.nom, equipe_b.nom,
            score_total_a, score_total_b,
            scores_a, scores_b, value_bet
        )
        
        return {
            'equipe_a': {
                'nom': equipe_a.nom,
                'scores': scores_a,
                'score_total': score_total_a
            },
            'equipe_b': {
                'nom': equipe_b.nom,
                'scores': scores_b,
                'score_total': score_total_b
            },
            'decision': decision,
            'rapport': '\n'.join(self.rapport)
        }
    
    def _analyser_equipe(self, equipe: EquipeData) -> Dict[str, float]:
        """Analyse complète d'une équipe"""
        scores = {}
        
        # Module 1: IFP
        scores['ifp'] = self._calculer_ifp(equipe)
        
        # Module 2: Force offensive et défensive
        scores['force_offensive'], scores['solidite_defensive'] = \
            self._calculer_force_offensive_defensive(equipe)
        
        # Module 3: Facteur domicile/extérieur
        scores['facteur_domicile'] = self._calculer_facteur_domicile(equipe)
        
        # Module 4: Fatigue
        scores['fatigue'] = self._calculer_fatigue(equipe)
        
        # Module 5: Motivation
        scores['motivation'] = self._calculer_motivation(equipe)
        
        # Module 6: Impact des absences
        scores['absences'] = self._calculer_impact_absences(equipe)
        
        return scores
    
    def _calculer_ifp(self, equipe: EquipeData) -> float:
        """
        Module 1: Indice de Forme Pondéré
        """
        if len(equipe.matchs_historique) < 10:
            self._log(f"⚠️  Attention: Seulement {len(equipe.matchs_historique)} matchs disponibles (10 recommandés)")
        
        total_ifp = 0
        matchs = equipe.matchs_historique[:10]  # 10 derniers matchs
        
        for i, match in enumerate(matchs):
            # Points gagnés
            points = {'V': 3, 'N': 1, 'D': 0}.get(match.resultat, 0)
            
            # Coefficient adversaire
            if match.adversaire_classement <= 5:
                coef_adv = 1.3
            elif match.adversaire_classement <= 12:
                coef_adv = 1.0
            else:
                coef_adv = 0.8
            
            # Coefficient localisation
            if match.domicile == equipe.est_domicile:
                coef_loc = 1.1
            else:
                coef_loc = 0.95
            
            # Coefficient récence (match le plus récent = 1.5, le plus ancien = 0.6)
            coef_recence = 1.5 - (i * 0.1)
            
            # Coefficient compétition
            coef_comp = 1.0 if match.competition == 'Championnat' else 0.7
            
            ifp_match = points * coef_adv * coef_loc * coef_recence * coef_comp
            total_ifp += ifp_match
        
        ifp_moyen = total_ifp / len(matchs)
        
        # Déterminer le niveau de forme
        if ifp_moyen > 2.5:
            forme = FormLevel.EXCELLENTE
        elif ifp_moyen >= 1.8:
            forme = FormLevel.BONNE
        elif ifp_moyen >= 1.2:
            forme = FormLevel.MOYENNE
        elif ifp_moyen >= 0.8:
            forme = FormLevel.FAIBLE
        else:
            forme = FormLevel.CRITIQUE
        
        self._log(f"IFP: {ifp_moyen:.2f} - Forme: {forme.value}")
        return ifp_moyen
    
    def _calculer_force_offensive_defensive(self, equipe: EquipeData) -> Tuple[float, float]:
        """
        Module 2: Force Offensive et Solidité Défensive
        """
        matchs = equipe.matchs_historique[:10]
        
        total_buts = 0
        total_xg = 0
        total_tirs = 0
        total_buts_encaisses = 0
        total_xg_contre = 0
        total_corners_concedes = 0
        
        for match in matchs:
            # Pondération selon adversaire
            if match.adversaire_classement <= 5:
                pond = 1.4
            elif match.adversaire_classement <= 12:
                pond = 1.0
            else:
                pond = 0.7
            
            total_buts += match.buts_pour * pond
            total_xg += match.xg_pour * pond
            total_tirs += match.tirs_cadres * pond
            total_buts_encaisses += match.buts_contre * pond
            total_xg_contre += match.xg_contre * pond
            total_corners_concedes += match.corners_concedes * pond
        
        nb_matchs = len(matchs)
        
        # Force Offensive
        fo = (total_buts / nb_matchs * 0.4) + \
             (total_xg / nb_matchs * 0.4) + \
             (total_tirs / nb_matchs * 0.2)
        
        # Solidité Défensive
        sd = 10 - ((total_buts_encaisses / nb_matchs * 0.5) + \
                   (total_xg_contre / nb_matchs * 0.3) + \
                   (total_corners_concedes / nb_matchs / 10 * 0.2))
        
        sd = max(0, min(10, sd))  # Limiter entre 0 et 10
        
        self._log(f"Force Offensive: {fo:.2f}/10")
        self._log(f"Solidité Défensive: {sd:.2f}/10")
        
        return fo, sd
    
    def _calculer_facteur_domicile(self, equipe: EquipeData) -> float:
        """
        Module 3: Facteur Domicile/Extérieur Personnalisé
        """
        if equipe.points_exterieur_saison == 0:
            ratio = 2.0
        else:
            ratio = equipe.points_domicile_saison / equipe.points_exterieur_saison
        
        if equipe.est_domicile:
            if ratio > 1.5:
                bonus = 0.8
                msg = "Équipe très dépendante de son public"
            elif ratio >= 1.2:
                bonus = 0.5
                msg = "Avantage domicile normal"
            elif ratio >= 0.8:
                bonus = 0.3
                msg = "Équipe homogène"
            else:
                bonus = 0.0
                msg = "Équipe meilleure à l'extérieur"
        else:
            # À l'extérieur, inverser la logique
            if ratio > 1.5:
                bonus = -0.3
                msg = "Équipe faible à l'extérieur"
            elif ratio >= 1.2:
                bonus = 0.0
                msg = "Performance extérieure correcte"
            else:
                bonus = 0.3
                msg = "Équipe performante à l'extérieur"
        
        self._log(f"Facteur Domicile/Extérieur: {bonus:+.1f} ({msg})")
        self._log(f"  Ratio D/E: {ratio:.2f}")
        
        return bonus
    
    def _calculer_fatigue(self, equipe: EquipeData) -> float:
        """
        Module 4: Gestion du Calendrier et Fatigue
        """
        score_fatigue = 0
        
        self._log(f"Analyse du calendrier:")
        
        # Matchs récents (7 derniers jours)
        for match in equipe.calendrier_avant:
            if match.competition == 'Coupe d\'Europe':
                score_fatigue -= 1.5
                self._log(f"  - Match européen récent: -1.5")
            elif match.competition == 'Coupe nationale':
                score_fatigue -= 0.8
                self._log(f"  - Match de coupe récent: -0.8")
            elif match.distance_km > 500:
                score_fatigue -= 0.5
                self._log(f"  - Long déplacement ({match.distance_km}km): -0.5")
            else:
                score_fatigue -= 0.3
                self._log(f"  - Match de championnat: -0.3")
        
        # Matchs à venir (7 prochains jours)
        for match in equipe.calendrier_apres:
            if match.importance == 'Crucial':
                score_fatigue -= 1.0
                self._log(f"  - Match crucial à venir: -1.0")
            elif match.competition == 'Coupe d\'Europe':
                score_fatigue -= 0.7
                self._log(f"  - Match européen à venir: -0.7")
        
        # Conversion en bonus/malus
        if score_fatigue > -2:
            impact = 0
            msg = "Pas de fatigue significative"
        elif score_fatigue >= -4:
            impact = -0.3
            msg = "Fatigue modérée"
        else:
            impact = -0.8
            msg = "Fatigue importante"
        
        self._log(f"Score fatigue: {score_fatigue:.1f} → Impact: {impact} ({msg})")
        
        return impact
    
    def _calculer_motivation(self, equipe: EquipeData) -> float:
        """
        Module 5: Enjeu et Motivation
        """
        score_motivation = 0
        details = []
        
        # A. Situation au classement
        if equipe.situation == 'Titre':
            if abs(equipe.points_du_leader) <= 5:
                score_motivation += 3
                details.append("Lutte pour le titre (+3)")
        elif equipe.situation == 'Europe':
            score_motivation += 2
            details.append("Course à l'Europe (+2)")
        elif equipe.situation == 'Maintien':
            score_motivation += 2.5
            details.append("Lutte pour le maintien (+2.5)")
        elif equipe.situation == 'Relégué':
            score_motivation -= 2
            details.append("Déjà relégué (-2)")
        elif equipe.situation == 'Champion':
            score_motivation -= 2
            details.append("Déjà champion (-2)")
        else:
            details.append("Milieu de tableau (0)")
        
        # B. Séquence de résultats
        if equipe.serie_actuelle:
            if 'D' in equipe.serie_actuelle and equipe.serie_actuelle.count('D') >= 3:
                score_motivation += 1
                details.append("Besoin de réagir après 3 défaites (+1)")
            elif 'V' in equipe.serie_actuelle and equipe.serie_actuelle.count('V') >= 5:
                score_motivation += 0.5
                details.append("Sur une série de victoires (+0.5)")
        
        # C. Contexte émotionnel
        if equipe.derby:
            score_motivation += 1.5
            details.append("Derby local (+1.5)")
        
        # D. Situation entraîneur
        if equipe.entraîneur_nouveau:
            score_motivation += 0.5
            details.append("Effet nouveau coach (+0.5)")
        elif equipe.entraîneur_sous_pression:
            score_motivation += 0.8
            details.append("Entraîneur sous pression (+0.8)")
        
        self._log(f"Score Motivation: {score_motivation:+.1f}")
        for detail in details:
            self._log(f"  - {detail}")
        
        return score_motivation
    
    def _calculer_impact_absences(self, equipe: EquipeData) -> float:
        """
        Module 6: Impact des Absences
        """
        if not equipe.joueurs_absents:
            self._log("Aucune absence signalée")
            return 0
        
        perte_totale = sum(j.importance for j in equipe.joueurs_absents)
        
        self._log(f"Joueurs absents:")
        for joueur in equipe.joueurs_absents:
            self._log(f"  - {joueur.nom} ({joueur.poste}): {joueur.importance}/10")
        
        if perte_totale > 15:
            impact = -1.5
            msg = "Impact MAJEUR"
        elif perte_totale >= 10:
            impact = -1.0
            msg = "Impact Important"
        elif perte_totale >= 5:
            impact = -0.5
            msg = "Impact Modéré"
        else:
            impact = -0.2
            msg = "Impact Mineur"
        
        self._log(f"Perte totale: {perte_totale}/10 → {impact} ({msg})")
        
        return impact
    
    def _analyser_h2h(self, h2h: HistoriqueH2H, nom_a: str, nom_b: str) -> Dict:
        """
        Module 7: Historique des Confrontations Directes
        """
        total_matchs = h2h.victoires_equipe_a + h2h.nuls + h2h.victoires_equipe_b
        
        self._log(f"Bilan sur {total_matchs} derniers matchs:")
        self._log(f"  {nom_a}: {h2h.victoires_equipe_a} victoires")
        self._log(f"  Nuls: {h2h.nuls}")
        self._log(f"  {nom_b}: {h2h.victoires_equipe_b} victoires")
        
        bonus_a = 0
        bonus_b = 0
        
        # Tendance récente (5 derniers)
        if len(h2h.derniers_gagnants) >= 3:
            count_a = h2h.derniers_gagnants.count('A')
            count_b = h2h.derniers_gagnants.count('B')
            
            if count_a >= 3:
                bonus_a = 0.5
                self._log(f"  → {nom_a} domine les confrontations récentes (+0.5)")
            elif count_b >= 3:
                bonus_b = 0.5
                self._log(f"  → {nom_b} domine les confrontations récentes (+0.5)")
        
        # Matchs serrés
        if h2h.matchs_serres >= total_matchs * 0.7:
            self._log(f"  → Historique de matchs serrés (bonus pour Sous 2.5 buts)")
        
        # Domination psychologique
        if h2h.victoires_equipe_a == 0 and total_matchs >= 5:
            bonus_b = 1.0
            self._log(f"  → {nom_b} invaincu sur {total_matchs} matchs (facteur psychologique +1.0)")
        elif h2h.victoires_equipe_b == 0 and total_matchs >= 5:
            bonus_a = 1.0
            self._log(f"  → {nom_a} invaincu sur {total_matchs} matchs (facteur psychologique +1.0)")
        
        return {'equipe_a': bonus_a, 'equipe_b': bonus_b}
    
    def _calculer_score_total(self, scores: Dict[str, float]) -> float:
        """Calcul du score total pondéré"""
        total = 0
        for module, poids in self.POIDS.items():
            if module in scores:
                total += scores[module] * poids
        return total
    
    def _analyser_marche(self, cotes: CotesMarche, score_a: float, score_b: float) -> Dict:
        """
        Module 8: Analyse du Marché
        """
        # Probabilités implicites
        prob_a = 1 / cotes.victoire_equipe_a
        prob_nul = 1 / cotes.nul
        prob_b = 1 / cotes.victoire_equipe_b
        
        # Marge du bookmaker
        marge = (prob_a + prob_nul + prob_b - 1) * 100
        
        self._log(f"Cotes du marché:")
        self._log(f"  Équipe A: {cotes.victoire_equipe_a:.2f} (proba: {prob_a*100:.1f}%)")
        self._log(f"  Nul: {cotes.nul:.2f} (proba: {prob_nul*100:.1f}%)")
        self._log(f"  Équipe B: {cotes.victoire_equipe_b:.2f} (proba: {prob_b*100:.1f}%)")
        self._log(f"  Marge bookmaker: {marge:.1f}%")
        
        # Probabilité selon notre modèle (simplifiée)
        ecart = score_a - score_b
        notre_prob_a = 0.5 + (ecart * 0.1)  # Ajustement simplifié
        notre_prob_a = max(0.1, min(0.9, notre_prob_a))  # Limiter entre 10% et 90%
        
        # Value bet
        value_a = (notre_prob_a - prob_a) * 100
        value_b = ((1 - notre_prob_a) - prob_b) * 100
        
        self._log(f"\nNotre analyse:")
        self._log(f"  Probabilité Équipe A: {notre_prob_a*100:.1f}%")
        self._log(f"  Probabilité Équipe B: {(1-notre_prob_a)*100:.1f}%")
        
        value_bet = None
        if value_a > 10:
            self._log(f"\n✅ VALUE BET détectée sur Équipe A (+{value_a:.1f}%)")
            value_bet = {'equipe': 'A', 'value': value_a}
        elif value_b > 10:
            self._log(f"\n✅ VALUE BET détectée sur Équipe B (+{value_b:.1f}%)")
            value_bet = {'equipe': 'B', 'value': value_b}
        else:
            self._log(f"\n❌ Pas de value bet claire")
        
        # Mouvement de cotes
        if cotes.cote_initiale_equipe_a > 0:
            mouvement_a = ((cotes.victoire_equipe_a - cotes.cote_initiale_equipe_a) / 
                          cotes.cote_initiale_equipe_a * 100)
            if abs(mouvement_a) > 10:
                self._log(f"\n⚠️  Mouvement de cote important sur Équipe A: {mouvement_a:+.1f}%")
        
        return value_bet
    
    def _generer_decision(self, nom_a: str, nom_b: str, 
                         score_a: float, score_b: float,
                         scores_a: Dict, scores_b: Dict,
                         value_bet: Optional[Dict]) -> Dict:
        """
        Phase 6: Génération de la décision finale
        """
        ecart = abs(score_a - score_b)
        
        self._log(f"\nSCORE TOTAL {nom_a}: {score_a:.2f}")
        self._log(f"SCORE TOTAL {nom_b}: {score_b:.2f}")
        self._log(f"ÉCART: {ecart:.2f}")
        
        # Déterminer le niveau de confiance
        if ecart > 2.5:
            confiance = ConfidenceLevel.FORTE_CONFIANCE
            mise_pct = "3-5%"
        elif ecart >= 1.5:
            confiance = ConfidenceLevel.CONFIANCE_MODEREE
            mise_pct = "2-3%"
        elif ecart >= 0.5:
            confiance = ConfidenceLevel.MATCH_SERRE
            mise_pct = "1%"
        else:
            confiance = ConfidenceLevel.INCERTITUDE
            mise_pct = "0% - NE PAS PARIER"
        
        # Pronostic
        if score_a > score_b:
            favori = nom_a
            outsider = nom_b
        else:
            favori = nom_b
            outsider = nom_a
        
        if confiance == ConfidenceLevel.FORTE_CONFIANCE:
            pronostic = f"Victoire {favori}"
            alt_pronostic = f"Double Chance {favori}"
        elif confiance == ConfidenceLevel.CONFIANCE_MODEREE:
            pronostic = f"Victoire {favori} ou Double Chance"
            alt_pronostic = None
        elif confiance == ConfidenceLevel.MATCH_SERRE:
            pronostic = "Match nul / Double Chance / Sous-Over buts"
            alt_pronostic = None
        else:
            pronostic = "NE PAS PARIER"
            alt_pronostic = "Match trop incertain"
        
        self._log(f"\n{'='*80}")
        self._log(f"🎯 DÉCISION FINALE")
        self._log(f"{'='*80}")
        self._log(f"Niveau de confiance: {confiance.value}")
        self._log(f"Pronostic: {pronostic}")
        if alt_pronostic:
            self._log(f"Alternative: {alt_pronostic}")
        self._log(f"Mise recommandée: {mise_pct} de la bankroll")
        
        if value_bet:
            self._log(f"\n💎 Value Bet identifiée: Équipe {value_bet['equipe']} (+{value_bet['value']:.1f}%)")
        
        # Recommandation finale
        if confiance == ConfidenceLevel.INCERTITUDE:
            recommandation = "❌ NE PAS PARIER - Trop d'incertitude"
        elif confiance == ConfidenceLevel.MATCH_SERRE and not value_bet:
            recommandation = "⚠️  Parier avec prudence (1% max)"
        elif value_bet and ecart >= 1.5:
            recommandation = "✅ BON PARI - Confiance + Value bet"
        elif ecart >= 2.5:
            recommandation = "✅ EXCELLENT PARI - Forte confiance"
        else:
            recommandation = "⚡ Pari possible mais sélectif"
        
        self._log(f"\n{recommandation}")
        self._log(f"{'='*80}")
        
        return {
            'favori': favori,
            'ecart_score': ecart,
            'confiance': confiance.value,
            'pronostic': pronostic,
            'pronostic_alternatif': alt_pronostic,
            'mise_recommandee': mise_pct,
            'value_bet': value_bet,
            'recommandation': recommandation,
            'parier': confiance != ConfidenceLevel.INCERTITUDE
        }
    
    def _log(self, message: str):
        """Ajouter une ligne au rapport"""
        self.rapport.append(message)
        print(message)


def exemple_utilisation():
    """
    Exemple d'utilisation du système APEX-30
    """
    print("\n" + "="*80)
    print("EXEMPLE D'ANALYSE - SYSTÈME APEX-30")
    print("="*80 + "\n")
    
    # Création des données pour l'Équipe A (ex: PSG à domicile)
    matchs_psg = [
        MatchData("2025-01-20", False, "V", 3, 1, 8, "Championnat", 2.8, 0.9, 62, 8, 6, 3),
        MatchData("2025-01-15", True, "V", 2, 0, 12, "Championnat", 2.2, 0.5, 58, 7, 7, 2),
        MatchData("2025-01-12", False, "N", 1, 1, 3, "Coupe d'Europe", 1.5, 1.8, 48, 4, 5, 6),
        MatchData("2025-01-08", True, "V", 4, 1, 15, "Championnat", 3.5, 0.8, 65, 10, 9, 2),
        MatchData("2025-01-05", False, "D", 1, 2, 2, "Championnat", 1.2, 2.3, 45, 3, 4, 7),
        MatchData("2024-12-22", True, "V", 3, 0, 10, "Championnat", 2.9, 0.4, 60, 9, 8, 1),
        MatchData("2024-12-18", False, "V", 2, 1, 6, "Coupe nationale", 2.0, 1.1, 55, 6, 6, 4),
        MatchData("2024-12-15", True, "N", 2, 2, 4, "Championnat", 2.5, 1.9, 57, 7, 7, 5),
        MatchData("2024-12-11", False, "V", 1, 0, 9, "Championnat", 1.8, 0.6, 52, 5, 5, 3),
        MatchData("2024-12-08", True, "V", 3, 1, 11, "Championnat", 2.7, 1.0, 61, 8, 7, 3),
    ]
    
    equipe_a = EquipeData(
        nom="Paris SG",
        matchs_historique=matchs_psg,
        classement_actuel=1,
        points_domicile_saison=2.5,
        points_exterieur_saison=1.9,
        est_domicile=True,
        calendrier_avant=[
            MatchAVenir("2025-01-23", "Championnat", "Normal", 0)
        ],
        calendrier_apres=[
            MatchAVenir("2025-01-31", "Coupe d'Europe", "Important", 800)
        ],
        joueurs_absents=[
            JoueurAbsent("Mbappé", "Attaquant", 9, 5)
        ],
        points_du_leader=0,
        situation="Titre",
        serie_actuelle="3V1N",
        entraîneur_nouveau=False,
        entraîneur_sous_pression=False,
        derby=False
    )
    
    # Création des données pour l'Équipe B (ex: Lyon à l'extérieur)
    matchs_lyon = [
        MatchData("2025-01-21", True, "V", 2, 1, 14, "Championnat", 1.9, 1.2, 51, 6, 5, 4),
        MatchData("2025-01-17", False, "D", 0, 1, 5, "Championnat", 0.8, 1.6, 43, 2, 3, 6),
        MatchData("2025-01-13", True, "N", 1, 1, 9, "Championnat", 1.4, 1.3, 49, 4, 6, 5),
        MatchData("2025-01-10", False, "D", 1, 3, 2, "Coupe nationale", 1.1, 2.8, 38, 3, 4, 8),
        MatchData("2025-01-06", True, "V", 2, 0, 13, "Championnat", 2.1, 0.7, 55, 7, 7, 2),
        MatchData("2024-12-23", False, "D", 0, 2, 4, "Championnat", 0.9, 2.2, 41, 2, 3, 7),
        MatchData("2024-12-19", True, "V", 3, 2, 11, "Championnat", 2.6, 1.8, 53, 8, 8, 5),
        MatchData("2024-12-16", False, "N", 1, 1, 7, "Championnat", 1.2, 1.4, 46, 4, 5, 6),
        MatchData("2024-12-12", True, "D", 1, 2, 3, "Coupe d'Europe", 1.3, 2.1, 44, 3, 4, 7),
        MatchData("2024-12-09", False, "V", 2, 1, 15, "Championnat", 1.7, 1.1, 48, 5, 6, 4),
    ]
    
    equipe_b = EquipeData(
        nom="Olympique Lyonnais",
        matchs_historique=matchs_lyon,
        classement_actuel=7,
        points_domicile_saison=1.8,
        points_exterieur_saison=1.2,
        est_domicile=False,
        calendrier_avant=[
            MatchAVenir("2025-01-24", "Coupe d'Europe", "Important", 600)
        ],
        calendrier_apres=[],
        joueurs_absents=[
            JoueurAbsent("Lacazette", "Attaquant", 7, 2),
            JoueurAbsent("Tolisso", "Milieu", 5, 10)
        ],
        points_du_leader=-18,
        situation="Europe",
        serie_actuelle="1V1D1N",
        entraîneur_nouveau=False,
        entraîneur_sous_pression=True,
        derby=False
    )
    
    # Historique H2H
    h2h = HistoriqueH2H(
        victoires_equipe_a=3,
        nuls=1,
        victoires_equipe_b=1,
        matchs_serres=3,
        derniers_gagnants=['A', 'N', 'A', 'B', 'A']
    )
    
    # Cotes du marché
    cotes = CotesMarche(
        victoire_equipe_a=1.65,
        nul=3.80,
        victoire_equipe_b=5.50,
        cote_initiale_equipe_a=1.70,
        cote_initiale_equipe_b=5.20
    )
    
    # Analyse
    analyzer = APEX30Analyzer()
    resultat = analyzer.analyser_match(equipe_a, equipe_b, h2h, cotes)
    
    # Sauvegarde du rapport
    with open('/home/claude/rapport_analyse.txt', 'w', encoding='utf-8') as f:
        f.write(resultat['rapport'])
    
    print("\n✅ Rapport complet sauvegardé dans: rapport_analyse.txt")
    
    return resultat


if __name__ == "__main__":
    # Lancer l'exemple
    resultat = exemple_utilisation()
    
    # Afficher le JSON du résultat
    print("\n" + "="*80)
    print("RÉSULTAT JSON")
    print("="*80)
    print(json.dumps({
        'equipe_a': {
            'nom': resultat['equipe_a']['nom'],
            'score_total': round(resultat['equipe_a']['score_total'], 2)
        },
        'equipe_b': {
            'nom': resultat['equipe_b']['nom'],
            'score_total': round(resultat['equipe_b']['score_total'], 2)
        },
        'decision': resultat['decision']
    }, indent=2, ensure_ascii=False))
