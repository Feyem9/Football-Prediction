"""
APEX-30 Service - Intégration du Système Professionnel de Pronostic
Adapté pour Pronoscore à partir du système original APEX-30

Ce service remplace "Ma Logique" avec une approche scientifique basée sur 10 modules (v2.0).
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from sqlalchemy.orm import Session


class FormLevel(Enum):
    """Niveaux de forme d'une équipe"""
    CRITIQUE = "Critique"
    FAIBLE = "Faible"
    MOYENNE = "Moyenne"
    BONNE = "Bonne"
    EXCELLENTE = "Excellente"


class ConfidenceLevel(Enum):
    """Niveaux de confiance du pronostic"""
    INCERTITUDE = "Incertitude"
    MATCH_SERRE = "Match serré"
    CONFIANCE_MODEREE = "Confiance modérée"
    FORTE_CONFIANCE = "Forte confiance"


@dataclass
class MatchHistorique:
    """Données d'un match passé pour l'analyse de forme"""
    date: datetime
    domicile: bool
    resultat: str  # 'V', 'N', 'D'
    buts_pour: int
    buts_contre: int
    adversaire_classement: int  # Position au classement (1-20)
    competition: str  # 'Championnat', 'Coupe'


@dataclass
class EquipeAnalyse:
    """Données d'équipe pour l'analyse APEX-30"""
    nom: str
    matchs_historique: List[MatchHistorique]
    classement_actuel: int
    points_domicile_saison: float
    points_exterieur_saison: float
    est_domicile: bool
    situation: str = "Milieu de tableau"  # 'Titre', 'Europe', 'Maintien', etc.


@dataclass
class H2HStats:
    """Statistiques des confrontations directes"""
    victoires_a: int
    nuls: int
    victoires_b: int
    derniers_gagnants: List[str]  # ['A', 'B', 'N']


class APEX30Service:
    """
    Service APEX-30 v2.0 adapté pour Pronoscore
    Analyse les matchs selon 10 modules pondérés
    
    Améliorations v2.0:
    - Ajout module xG simulé (Expected Goals)
    - Ajout module Tendance récente (3 derniers matchs)
    - Rééquilibrage des poids selon analyse de performance
    """
    
    # Coefficients de pondération v2.0 (total = 1.0)
    # Optimisés selon les recommandations du guide d'amélioration APEX-30
    POIDS = {
        'ifp': 0.20,                # Indice de Forme Pondéré (réduit car tendance_recente prend le relais)
        'force_offensive': 0.12,    # Force offensive
        'solidite_defensive': 0.12, # Solidité défensive
        'facteur_domicile': 0.12,   # Avantage domicile (augmenté - très prédictif)
        'fatigue': 0.05,            # Fatigue (calendrier)
        'motivation': 0.13,         # Enjeu et motivation (légèrement réduit)
        'absences': 0.06,           # Impact absences
        'h2h': 0.08,                # Historique H2H
        'xg_simule': 0.07,          # NOUVEAU: Expected Goals simulé
        'tendance_recente': 0.05    # NOUVEAU: Tendance 3 derniers matchs
    }
    
    def __init__(self, db: Session):
        self.db = db
        self.rapport = []
    
    def analyser_match(
        self,
        equipe_a: EquipeAnalyse,
        equipe_b: EquipeAnalyse,
        h2h: H2HStats,
        injuries_a: List[Dict] = None,
        injuries_b: List[Dict] = None
    ) -> Dict:
        """
        Analyse complète d'un match avec APEX-30
        
        Args:
            equipe_a: Données de l'équipe domicile
            equipe_b: Données de l'équipe extérieur
            h2h: Statistiques des confrontations directes
            injuries_a: Liste des blessures équipe domicile
            injuries_b: Liste des blessures équipe extérieur
        
        Returns:
            Dictionnaire avec scores, prédiction et confiance
        """
        self.rapport = []
        
        # Phase 1: Analyser équipe A (avec blessures)
        print(f"DEBUG APEX: Analysing {equipe_a.nom}...")
        scores_a = self._analyser_equipe(equipe_a, injuries_a)
        
        # Phase 2: Analyser équipe B (avec blessures)
        print(f"DEBUG APEX: Analysing {equipe_b.nom}...")
        scores_b = self._analyser_equipe(equipe_b, injuries_b)
        
        # Phase 3: Analyser H2H
        print(f"DEBUG APEX: Analysing H2H...")
        h2h_scores = self._analyser_h2h(h2h, equipe_a.nom, equipe_b.nom)
        scores_a['h2h'] = h2h_scores['equipe_a']
        scores_b['h2h'] = h2h_scores['equipe_b']
        
        # Phase 4: Calculer scores totaux
        score_total_a = self._calculer_score_total(scores_a)
        score_total_b = self._calculer_score_total(scores_b)
        print(f"DEBUG APEX: Total scores calculated: {score_total_a} vs {score_total_b}")
        
        # Phase 5: Générer décision
        decision = self._generer_decision(
            equipe_a.nom, equipe_b.nom,
            score_total_a, score_total_b,
            scores_a, scores_b
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
    
    def _analyser_equipe(self, equipe: EquipeAnalyse, injuries: List[Dict] = None) -> Dict[str, float]:
        """Analyse complète d'une équipe (10 modules v2.0)"""
        scores = {}
        
        # Module 1: IFP (Indice de Forme Pondéré)
        scores['ifp'] = self._calculer_ifp(equipe)
        
        # Module 2: Force offensive et défensive
        fo, sd = self._calculer_force_offensive_defensive(equipe)
        scores['force_offensive'] = fo
        scores['solidite_defensive'] = sd
        
        # Module 3: Facteur domicile/extérieur
        scores['facteur_domicile'] = self._calculer_facteur_domicile(equipe)
        
        # Module 4: Fatigue (simplifié - basé sur nombre de matchs récents)
        scores['fatigue'] = self._calculer_fatigue(equipe)
        
        # Module 5: Motivation
        scores['motivation'] = self._calculer_motivation(equipe)
        
        # Module 6: Absences (blessures/suspensions)
        scores['absences'] = self._calculer_absences(equipe, injuries)
        
        # Module 9: xG Simulé (Expected Goals)
        scores['xg_simule'] = self._calculer_xg_simule(equipe)
        
        # Module 10: Tendance Récente (Momentum)
        scores['tendance_recente'] = self._calculer_tendance_recente(equipe)
        
        return scores
    
    def _calculer_absences(self, equipe: EquipeAnalyse, injuries: List[Dict] = None) -> float:
        """
        Module 6: Impact des Absences (Blessures/Suspensions)
        
        Calcule l'impact négatif des joueurs absents sur l'équipe.
        Plus il y a de joueurs clés absents, plus le malus est important.
        """
        if not injuries or len(injuries) == 0:
            self._log(f"Absences {equipe.nom}: 0 (pas de blessures connues)")
            return 0  # Neutre
        
        malus = 0
        nb_blesses = len(injuries)
        
        for injury in injuries:
            importance = injury.get('importance', 5)  # 1-10
            poste = injury.get('poste', 'Joueur').lower()
            
            # Pondération selon le poste
            if 'gardien' in poste or 'goalkeeper' in poste:
                coef_poste = 1.5  # Gardien très important
            elif 'attaquant' in poste or 'striker' in poste or 'forward' in poste:
                coef_poste = 1.3  # Attaquant crucial
            elif 'milieu' in poste or 'midfielder' in poste:
                coef_poste = 1.1
            else:
                coef_poste = 1.0
            
            # Pondération selon l'importance (1-10)
            coef_importance = importance / 10.0
            
            # Malus par joueur (max -0.3 par joueur clé)
            malus -= (0.15 * coef_poste * coef_importance)
        
        # Malus global si beaucoup de blessés
        if nb_blesses >= 5:
            malus -= 0.3  # Beaucoup de blessés = équipe affaiblie
        elif nb_blesses >= 3:
            malus -= 0.15
        
        # Plafonner le malus à -1.5
        malus = max(-1.5, malus)
        
        self._log(f"Absences {equipe.nom}: {malus:.2f} ({nb_blesses} blessés)")
        
        return malus
    
    def _calculer_xg_simule(self, equipe: EquipeAnalyse) -> float:
        """
        Module 9: Expected Goals (xG) Simulé
        
        Estime la qualité des occasions créées en comparant:
        - Buts marqués vs moyenne de tirs
        - Efficacité offensive
        
        Un xG positif signifie que l'équipe surperforme (bonne finition)
        Un xG négatif signifie que l'équipe sous-performe (mauvaise finition)
        """
        if not equipe.matchs_historique:
            return 0.0
        
        matchs = equipe.matchs_historique[:10]
        total_buts = 0
        total_matchs = len(matchs)
        
        for match in matchs:
            total_buts += match.buts_pour
        
        if total_matchs == 0:
            return 0.0
        
        # Moyenne de buts par match
        moy_buts = total_buts / total_matchs
        
        # xG attendu selon le niveau de l'équipe (basé sur classement)
        # Équipe top 5: ~2.0 xG/match attendu
        # Équipe milieu: ~1.2 xG/match attendu
        # Équipe bas: ~0.8 xG/match attendu
        if equipe.classement_actuel <= 5:
            xg_attendu = 2.0
        elif equipe.classement_actuel <= 10:
            xg_attendu = 1.5
        elif equipe.classement_actuel <= 15:
            xg_attendu = 1.2
        else:
            xg_attendu = 0.9
        
        # Différence xG réel vs attendu
        diff_xg = moy_buts - xg_attendu
        
        # Normaliser sur échelle -0.5 à +0.5
        score_xg = max(-0.5, min(0.5, diff_xg * 0.4))
        
        if score_xg > 0.2:
            msg = "surperforme (finition excellente)"
        elif score_xg > 0:
            msg = "légèrement au-dessus"
        elif score_xg > -0.2:
            msg = "dans la norme"
        else:
            msg = "sous-performe (doit améliorer finition)"
        
        self._log(f"xG Simulé {equipe.nom}: {score_xg:+.2f} ({msg})")
        
        return score_xg
    
    def _calculer_tendance_recente(self, equipe: EquipeAnalyse) -> float:
        """
        Module 10: Tendance Récente (Momentum)
        
        Analyse les 3 DERNIERS matchs uniquement pour capturer le momentum.
        Plus fiable que l'IFP car il détecte les équipes en feu.
        
        Calcule:
        - Série en cours (victoires/défaites consécutives)
        - Évolution de la forme (en hausse, stable, en baisse)
        """
        if not equipe.matchs_historique or len(equipe.matchs_historique) < 3:
            return 0.0
        
        # 3 derniers matchs seulement
        derniers_3 = equipe.matchs_historique[:3]
        
        score_momentum = 0
        victoires_consecutives = 0
        defaites_consecutives = 0
        
        for i, match in enumerate(derniers_3):
            poids = 1.3 if i == 0 else (1.1 if i == 1 else 1.0)  # Match le plus récent = plus important
            
            if match.resultat == 'V':
                score_momentum += 0.3 * poids
                if i == 0:
                    victoires_consecutives = 1
                    # Vérifier séries
                    for j in range(1, len(derniers_3)):
                        if derniers_3[j].resultat == 'V':
                            victoires_consecutives += 1
                        else:
                            break
            elif match.resultat == 'D':
                score_momentum -= 0.3 * poids
                if i == 0:
                    defaites_consecutives = 1
                    for j in range(1, len(derniers_3)):
                        if derniers_3[j].resultat == 'D':
                            defaites_consecutives += 1
                        else:
                            break
            # Nul = neutre
        
        # Bonus/Malus pour séries
        if victoires_consecutives >= 3:
            score_momentum += 0.4  # Série de feu!
            msg = "🔥 SÉRIE DE FEU (3V+)"
        elif victoires_consecutives >= 2:
            score_momentum += 0.2
            msg = "En forme (2V consécutives)"
        elif defaites_consecutives >= 3:
            score_momentum -= 0.4  # Crise!
            msg = "⚠️ CRISE (3D+)"
        elif defaites_consecutives >= 2:
            score_momentum -= 0.2
            msg = "En difficulté (2D consécutives)"
        else:
            msg = "Forme stable"
        
        # Plafonner
        score_momentum = max(-0.8, min(0.8, score_momentum))
        
        self._log(f"Tendance Récente {equipe.nom}: {score_momentum:+.2f} ({msg})")
        
        return score_momentum
    
    def _calculer_ifp(self, equipe: EquipeAnalyse) -> float:
        """
        Module 1: Indice de Forme Pondéré
        Analyse les 10 derniers matchs avec pondération
        """
        if not equipe.matchs_historique:
            return 1.0  # Valeur neutre
        
        total_ifp = 0
        matchs = equipe.matchs_historique[:10]  # 10 derniers matchs
        
        for i, match in enumerate(matchs):
            # Points gagnés
            points = {'V': 3, 'N': 1, 'D': 0}.get(match.resultat, 0)
            
            # Coefficient adversaire (selon classement)
            if match.adversaire_classement <= 5:
                coef_adv = 1.3  # Top 5 = plus de valeur
            elif match.adversaire_classement <= 12:
                coef_adv = 1.0  # Milieu de tableau
            else:
                coef_adv = 0.8  # Bas de tableau
            
            # Coefficient localisation
            if match.domicile == equipe.est_domicile:
                coef_loc = 1.1  # Situation similaire
            else:
                coef_loc = 0.95
            
            # Coefficient récence (match récent = plus important)
            coef_recence = 1.5 - (i * 0.1)  # De 1.5 à 0.6
            
            # Coefficient compétition
            coef_comp = 1.0 if match.competition == 'Championnat' else 0.8
            
            ifp_match = points * coef_adv * coef_loc * coef_recence * coef_comp
            total_ifp += ifp_match
        
        ifp_moyen = total_ifp / len(matchs) if matchs else 1.0
        
        self._log(f"IFP {equipe.nom}: {ifp_moyen:.2f}")
        
        return ifp_moyen
    
    def _calculer_force_offensive_defensive(self, equipe: EquipeAnalyse) -> Tuple[float, float]:
        """
        Module 2: Force Offensive et Solidité Défensive
        """
        if not equipe.matchs_historique:
            return 1.5, 5.0  # Valeurs neutres
        
        matchs = equipe.matchs_historique[:10]
        
        total_buts_pour = 0
        total_buts_contre = 0
        
        for match in matchs:
            # Pondération selon adversaire
            if match.adversaire_classement <= 5:
                pond = 1.4
            elif match.adversaire_classement <= 12:
                pond = 1.0
            else:
                pond = 0.7
            
            total_buts_pour += match.buts_pour * pond
            total_buts_contre += match.buts_contre * pond
        
        nb_matchs = len(matchs)
        
        # Force Offensive (buts moyens pondérés)
        fo = total_buts_pour / nb_matchs
        
        # Solidité Défensive (inverse des buts encaissés, échelle 0-10)
        buts_moy_contre = total_buts_contre / nb_matchs
        sd = max(0, min(10, 10 - (buts_moy_contre * 2)))
        
        self._log(f"Force Off. {equipe.nom}: {fo:.2f}, Solidité Déf.: {sd:.2f}")
        
        return fo, sd
    
    def _calculer_facteur_domicile(self, equipe: EquipeAnalyse) -> float:
        """
        Module 3: Facteur Domicile/Extérieur Personnalisé
        """
        if equipe.points_exterieur_saison == 0:
            ratio = 2.0
        else:
            ratio = equipe.points_domicile_saison / equipe.points_exterieur_saison
        
        if equipe.est_domicile:
            if ratio > 1.5:
                bonus = 0.8  # Très dépendant du public
            elif ratio >= 1.2:
                bonus = 0.5  # Avantage normal
            elif ratio >= 0.8:
                bonus = 0.3  # Homogène
            else:
                bonus = 0.0  # Meilleur à l'extérieur
        else:
            # À l'extérieur
            if ratio > 1.5:
                bonus = -0.3  # Faible à l'extérieur
            elif ratio >= 1.2:
                bonus = 0.0
            else:
                bonus = 0.3  # Performant à l'extérieur
        
        self._log(f"Facteur Dom. {equipe.nom}: {bonus:+.2f} (ratio D/E: {ratio:.2f})")
        
        return bonus
    
    def _calculer_fatigue(self, equipe: EquipeAnalyse) -> float:
        """
        Module 4: Gestion du Calendrier et Fatigue
        Simplifié - basé sur la densité de matchs récents
        """
        if not equipe.matchs_historique:
            return 0
        
        # Compter les matchs dans les 14 derniers jours
        import datetime as dt
        from datetime import timezone
        now = dt.datetime.now(timezone.utc)
        matchs_recents = 0
        
        for match in equipe.matchs_historique[:5]:
            # S'assurer que les deux sont aware pour la soustraction
            match_date = match.date
            if match_date.tzinfo is None:
                match_date = match_date.replace(tzinfo=timezone.utc)
            
            days_ago = (now - match_date).days
            if days_ago <= 14:
                matchs_recents += 1
        
        # Impact fatigue
        if matchs_recents >= 4:
            impact = -0.5  # Fatigue importante
        elif matchs_recents >= 3:
            impact = -0.3  # Fatigue modérée
        else:
            impact = 0  # Pas de fatigue
        
        self._log(f"Fatigue {equipe.nom}: {impact} ({matchs_recents} matchs récents)")
        
        return impact
    
    def _calculer_motivation(self, equipe: EquipeAnalyse) -> float:
        """
        Module 5: Enjeu et Motivation
        """
        score = 0
        
        # Situation au classement
        if equipe.situation == 'Titre':
            score += 2.0
        elif equipe.situation == 'Europe':
            score += 1.5
        elif equipe.situation == 'Maintien':
            score += 2.5  # Lutte pour le maintien = très motivé
        elif equipe.situation == 'Relégué':
            score -= 2.0  # Déjà relégué = démotivé
        
        # Bonus/malus selon classement
        if equipe.classement_actuel <= 3:
            score += 0.5  # Top 3 motivé
        elif equipe.classement_actuel >= 18:
            score += 1.0  # Zone rouge = survie
        
        self._log(f"Motivation {equipe.nom}: {score:+.2f} ({equipe.situation})")
        
        return score
    
    def _analyser_h2h(self, h2h: H2HStats, nom_a: str, nom_b: str) -> Dict:
        """
        Module 7: Historique des Confrontations Directes
        """
        bonus_a = 0
        bonus_b = 0
        
        total_matchs = h2h.victoires_a + h2h.nuls + h2h.victoires_b
        
        if total_matchs > 0:
            # Tendance générale
            if h2h.victoires_a > h2h.victoires_b * 2:
                bonus_a = 0.8
            elif h2h.victoires_a > h2h.victoires_b:
                bonus_a = 0.4
            elif h2h.victoires_b > h2h.victoires_a * 2:
                bonus_b = 0.8
            elif h2h.victoires_b > h2h.victoires_a:
                bonus_b = 0.4
            
            # Tendance récente (3 derniers)
            if len(h2h.derniers_gagnants) >= 3:
                count_a = h2h.derniers_gagnants[:3].count('A')
                count_b = h2h.derniers_gagnants[:3].count('B')
                
                if count_a >= 2:
                    bonus_a += 0.3
                elif count_b >= 2:
                    bonus_b += 0.3
            
            # Domination psychologique
            if h2h.victoires_a == 0 and total_matchs >= 5:
                bonus_b = 1.0  # B invaincu
            elif h2h.victoires_b == 0 and total_matchs >= 5:
                bonus_a = 1.0  # A invaincu
        
        self._log(f"H2H: {nom_a} +{bonus_a:.2f}, {nom_b} +{bonus_b:.2f}")
        
        return {'equipe_a': bonus_a, 'equipe_b': bonus_b}
    
    def _calculer_score_total(self, scores: Dict[str, float]) -> float:
        """Calcul du score total pondéré"""
        total = 0
        for module, poids in self.POIDS.items():
            if module in scores:
                total += scores[module] * poids
        return total
    
    def _generer_decision(
        self,
        nom_a: str,
        nom_b: str,
        score_a: float,
        score_b: float,
        scores_a: Dict,
        scores_b: Dict
    ) -> Dict:
        """Génération de la décision finale"""
        ecart = abs(score_a - score_b)
        
        # Déterminer confiance
        if ecart > 2.0:
            confiance = ConfidenceLevel.FORTE_CONFIANCE
            confiance_pct = 0.85
        elif ecart >= 1.0:
            confiance = ConfidenceLevel.CONFIANCE_MODEREE
            confiance_pct = 0.70
        elif ecart >= 0.4:
            confiance = ConfidenceLevel.MATCH_SERRE
            confiance_pct = 0.55
        else:
            confiance = ConfidenceLevel.INCERTITUDE
            confiance_pct = 0.40
        
        # Déterminer favori et scores
        if score_a > score_b:
            favori = nom_a
            outsider = nom_b
            diff = score_a - score_b
            # Prédire le score
            home_goals = round(1.5 + diff * 0.3)
            away_goals = round(max(0, 1.0 - diff * 0.2))
            winner = 'home'
            tip = f"Victoire {nom_a}"
        elif score_b > score_a:
            favori = nom_b
            outsider = nom_a
            diff = score_b - score_a
            home_goals = round(max(0, 1.0 - diff * 0.2))
            away_goals = round(1.5 + diff * 0.3)
            winner = 'away'
            tip = f"Victoire {nom_b}"
        else:
            favori = "Aucun"
            diff = 0
            home_goals = 1
            away_goals = 1
            winner = 'draw'
            tip = "Match nul"
        
        # Limiter les scores
        home_goals = max(0, min(5, home_goals))
        away_goals = max(0, min(5, away_goals))
        
        # Générer le tip
        total_goals = home_goals + away_goals
        if total_goals < 2:
            goals_tip = "Moins de 2.5 buts"
        elif total_goals > 3:
            goals_tip = "Plus de 2.5 buts"
        else:
            goals_tip = "Entre 2 et 3 buts"
        
        self._log(f"APEX-30: {nom_a} {score_a:.2f} vs {nom_b} {score_b:.2f}")
        self._log(f"Décision: {tip} ({confiance.value})")
        self._log(f"Score prédit: {home_goals}-{away_goals}")
        
        return {
            'favori': favori,
            'ecart_score': ecart,
            'confiance': confiance.value,
            'confiance_pct': confiance_pct,
            'pronostic': tip,
            'home_goals': home_goals,
            'away_goals': away_goals,
            'goals_tip': goals_tip,
            'winner': winner,
            'parier': confiance != ConfidenceLevel.INCERTITUDE,
            'scores_detail': {
                'equipe_a': scores_a,
                'equipe_b': scores_b
            }
        }
    
    def _log(self, message: str):
        """Ajouter au rapport"""
        self.rapport.append(message)

    def generer_rapport_detaille(self, analysis_data: Dict, home_name: str, away_name: str) -> List[Dict]:
        """
        Génère un rapport textuel professionnel basé sur les scores numériques.
        Utilisé pour l'affichage du tableau détaillé sur le front-end.
        """
        if not analysis_data or 'equipe_home' not in analysis_data:
            return []
            
        home_scores = analysis_data['equipe_home']
        away_scores = analysis_data['equipe_away']
        
        modules_info = [
            {
                'id': 'ifp',
                'nom': 'Indice de Forme Pondéré (IFP)',
                'poids': 20,
                'home_val': home_scores.get('ifp', 0),
                'away_val': away_scores.get('ifp', 0),
                'description': "Analyse la dynamique sur les 10 derniers matchs. Les victoires contre des équipes du Top 10 valent 1.3x plus que contre le bas de tableau."
            },
            {
                'id': 'force_offensive',
                'nom': 'Force Offensive',
                'poids': 12,
                'home_val': home_scores.get('force_offensive', 0),
                'away_val': away_scores.get('force_offensive', 0),
                'description': "Capacité à créer des occasions franches. Ce module pondère les buts marqués par le niveau de la défense adverse rencontrée."
            },
            {
                'id': 'solidite_defensive',
                'nom': 'Solidité Défensive',
                'poids': 12,
                'home_val': home_scores.get('solidite_defensive', 0),
                'away_val': away_scores.get('solidite_defensive', 0),
                'description': "Évalue la résistance du bloc. Une note de 8.4/10 indique une défense hermétique qui encaisse moins de 0.8 buts par match."
            },
            {
                'id': 'facteur_domicile',
                'nom': 'Loi Domicile / Extérieur',
                'poids': 12,
                'home_val': home_scores.get('facteur_domicile', 0),
                'away_val': away_scores.get('facteur_domicile', 0),
                'description': "Certaines équipes surperforment devant leur public (+0.5). Ce module ajuste le score selon le ratio points Domicile/Extérieur."
            },
            {
                'id': 'fatigue',
                'nom': 'Gestion Fatigue / Calendrier',
                'poids': 5,
                'home_val': home_scores.get('fatigue', 0),
                'away_val': away_scores.get('fatigue', 0),
                'description': "Impact physique basé sur le nombre de matchs joués en 14 jours. Un malus de -0.3 est appliqué dès le 4ème match consécutif."
            },
            {
                'id': 'motivation',
                'nom': 'Enjeu et Motivation',
                'poids': 13,
                'home_val': home_scores.get('motivation', 0),
                'away_val': away_scores.get('motivation', 0),
                'description': "Analyse situationnelle : lutte pour le titre, places européennes ou survie (maintien). Un bonus 'Survie' de +2.5 booste les outsiders."
            },
            {
                'id': 'absences',
                'nom': 'Impact Absences',
                'poids': 6,
                'home_val': home_scores.get('absences', 0),
                'away_val': away_scores.get('absences', 0),
                'description': "Pondère l'absence de joueurs cadres (capitaine, meilleur buteur) sur l'équilibre tactique global de l'équipe."
            },
            {
                'id': 'h2h',
                'nom': 'Historique H2H (Direct)',
                'poids': 8,
                'home_val': home_scores.get('h2h', 0),
                'away_val': away_scores.get('h2h', 0),
                'description': "Analyse l'ascendant psychologique historique. Une équipe qui reste sur 3 victoires en face-à-face reçoit un bonus de supériorité."
            },
            {
                'id': 'xg_simule',
                'nom': 'xG Simulé (Expected Goals)',
                'poids': 7,
                'home_val': home_scores.get('xg_simule', 0),
                'away_val': away_scores.get('xg_simule', 0),
                'description': "Estime si l'équipe surperforme ou sous-performe par rapport à son niveau attendu. Un score positif indique une finition efficace."
            },
            {
                'id': 'tendance_recente',
                'nom': 'Tendance Récente (Momentum)',
                'poids': 5,
                'home_val': home_scores.get('tendance_recente', 0),
                'away_val': away_scores.get('tendance_recente', 0),
                'description': "Capture le momentum des 3 derniers matchs. Détecte les séries de victoires (🔥) ou les crises (⚠️) en cours."
            }
        ]
        
        # Ajouter une explication personnalisée par module basée sur les valeurs
        for mod in modules_info:
            h = mod['home_val']
            a = mod['away_val']
            
            if mod['id'] == 'ifp':
                if h > a + 0.5:
                    mod['analyse'] = f"{home_name} arrive avec une dynamique nettement supérieure, portée par des résultats probants contre des adversaires de calibre."
                elif a > h + 0.5:
                    mod['analyse'] = f"{away_name} domine statistiquement cette période, avec une forme ascendante comparée à {home_name}."
                else:
                    mod['analyse'] = "Les deux formations affichent une dynamique de résultats similaire sur leurs 10 dernières sorties."
                    
            elif mod['id'] == 'force_offensive':
                if h > 2.0:
                    mod['analyse'] = f"L'attaque de {home_name} est en surchauffe, capable de percer n'importe quel bloc actuel."
                elif a > 2.0:
                    mod['analyse'] = f"{away_name} possède un potentiel offensif dévastateur, régulièrement en capacité de marquer plusieurs fois."
                else:
                    mod['analyse'] = "Potentiel offensif comparable entre les deux formations."
            
            elif mod['id'] == 'solidite_defensive':
                if h > 7 or a > 7:
                    mod['analyse'] = f"Sûreté défensive validée pour {home_name if h > a else away_name} qui concède très peu d'occasions franches."
                else:
                    mod['analyse'] = "Le match pourrait s'ouvrir suite à des approximations défensives de part et d'autre."
            
            elif mod['id'] == 'motivation':
                if h > 2.0 or a > 2.0:
                    mod['analyse'] = "L'enjeu est colossal pour ce match (Titre ou Maintien), ce qui garantit une intensité maximale."
                else:
                    mod['analyse'] = "Niveau de motivation standard pour un match de milieu de saison."
            
            elif mod['id'] == 'xg_simule':
                if h > 0.2:
                    mod['analyse'] = f"{home_name} fait preuve d'une efficacité redoutable devant le but, convertissant bien au-delà de la normale."
                elif a > 0.2:
                    mod['analyse'] = f"{away_name} surpasse son potentiel théorique avec une finition clinique."
                elif h < -0.2 or a < -0.2:
                    mod['analyse'] = "Une des deux équipes gaspille des occasions claires et devra améliorer sa finition."
                else:
                    mod['analyse'] = "Les deux équipes convertissent leurs occasions de manière conforme à leur niveau."
            
            elif mod['id'] == 'tendance_recente':
                if h > 0.6:
                    mod['analyse'] = f"🔥 {home_name} est en série de victoires! Momentum très favorable."
                elif a > 0.6:
                    mod['analyse'] = f"🔥 {away_name} enchaîne les victoires et arrive avec une confiance maximale."
                elif h < -0.4 or a < -0.4:
                    team_in_crisis = home_name if h < -0.4 else away_name
                    mod['analyse'] = f"⚠️ {team_in_crisis} traverse une crise de résultats inquiétante."
                else:
                    mod['analyse'] = "Les deux équipes affichent une forme récente stable."
            
            else:
                if h > a:
                    mod['analyse'] = f"Léger avantage pour {home_name} sur ce module spécifique."
                elif a > h:
                    mod['analyse'] = f"Avantage tactique détecté pour {away_name} selon ce paramètre."
                else:
                    mod['analyse'] = "Équilibre neutre sur ce facteur."

        return modules_info


# Fonction utilitaire pour créer les données à partir de nos modèles
def creer_h2h_stats(h2h_data: Dict) -> H2HStats:
    """
    Crée un objet H2HStats à partir des données brutes
    """
    return H2HStats(
        victoires_a=h2h_data.get('home_wins', 0),
        nuls=h2h_data.get('draws', 0),
        victoires_b=h2h_data.get('away_wins', 0),
        derniers_gagnants=h2h_data.get('recent_winners', [])
    )


def creer_equipe_analyse(
    nom: str,
    matchs_recents: List[Dict],
    classement: int,
    est_domicile: bool,
    points_domicile: float = 2.0,
    points_exterieur: float = 1.5
) -> EquipeAnalyse:
    """
    Crée un objet EquipeAnalyse à partir des données de l'API
    
    Supporte deux formats:
    1. Format API-Football: {resultat, buts_pour, buts_contre, domicile, adversaire, date}
    2. Format ancien: {score_home, score_away, home_team, match_date}
    
    Args:
        nom: Nom de l'équipe
        matchs_recents: Liste des 10 derniers matchs
        classement: Position au classement actuel
        est_domicile: True si joue à domicile pour ce match
        points_domicile: Points moyens par match à domicile
        points_exterieur: Points moyens par match à l'extérieur
    """
    matchs_historique = []
    
    for match in matchs_recents[:10]:
        # Vérifier si c'est le format API-Football (déjà traité)
        if 'resultat' in match and 'buts_pour' in match:
            # Format API-Football - déjà bien structuré
            resultat = match.get('resultat', 'N')
            buts_pour = match.get('buts_pour', 0) or 0
            buts_contre = match.get('buts_contre', 0) or 0
            domicile = match.get('domicile', True)
            
            # Date du match
            match_date = match.get('date')
            if isinstance(match_date, str):
                try:
                    match_date = datetime.fromisoformat(match_date.replace('Z', '+00:00'))
                except:
                    match_date = datetime.now() - timedelta(days=7)
            elif not isinstance(match_date, datetime):
                match_date = datetime.now() - timedelta(days=7)
            
            # Déterminer le classement adversaire (estimation si non disponible)
            adversaire_rank = match.get('adversaire_classement', 10)
            if adversaire_rank == 10:
                # Estimer le classement basé sur le résultat
                if resultat == 'V' and buts_pour > buts_contre + 1:
                    adversaire_rank = 12  # Adversaire plus faible
                elif resultat == 'D' and buts_contre > buts_pour + 1:
                    adversaire_rank = 5   # Adversaire plus fort
            
            competition = match.get('competition', 'Championnat')
            # Normaliser le type de compétition
            if 'Ligue' in competition or 'Premier' in competition or 'Serie' in competition or 'Liga' in competition or 'Bundesliga' in competition:
                competition = 'Championnat'
            elif 'Cup' in competition or 'Coupe' in competition:
                competition = 'Coupe'
            
        else:
            # Format ancien - convertir
            home_score = match.get('score_home', 0) or 0
            away_score = match.get('score_away', 0) or 0
            is_home = match.get('home_team', '') == nom or match.get('is_home', True)
            
            if is_home:
                buts_pour = home_score
                buts_contre = away_score
                domicile = True
            else:
                buts_pour = away_score
                buts_contre = home_score
                domicile = False
            
            if buts_pour > buts_contre:
                resultat = 'V'
            elif buts_pour < buts_contre:
                resultat = 'D'
            else:
                resultat = 'N'
            
            # Date du match
            from datetime import timezone
            match_date = match.get('match_date')
            if isinstance(match_date, str):
                try:
                    match_date = datetime.fromisoformat(match_date.replace('Z', '+00:00'))
                except:
                    match_date = datetime.now(timezone.utc) - timedelta(days=7)
            elif not isinstance(match_date, datetime):
                match_date = datetime.now(timezone.utc) - timedelta(days=7)
            
            if match_date.tzinfo is None:
                match_date = match_date.replace(tzinfo=timezone.utc)
            
            adversaire_rank = match.get('opponent_rank', 10)
            competition = match.get('competition', 'Championnat')
        
        matchs_historique.append(MatchHistorique(
            date=match_date,
            domicile=domicile,
            resultat=resultat,
            buts_pour=buts_pour,
            buts_contre=buts_contre,
            adversaire_classement=adversaire_rank,
            competition=competition
        ))
    
    # Déterminer la situation
    if classement <= 3:
        situation = 'Titre'
    elif classement <= 6:
        situation = 'Europe'
    elif classement >= 18:
        situation = 'Maintien'
    else:
        situation = 'Milieu de tableau'
    
    return EquipeAnalyse(
        nom=nom,
        matchs_historique=matchs_historique,
        classement_actuel=classement,
        points_domicile_saison=points_domicile,
        points_exterieur_saison=points_exterieur,
        est_domicile=est_domicile,
        situation=situation
    )


