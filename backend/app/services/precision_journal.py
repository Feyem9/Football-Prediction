"""
Journal de Précision - Vérification automatique des prédictions

Ce service vérifie les résultats réels des matchs et compare avec les prédictions
pour calculer le taux de réussite du système APEX-30.
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Dict
import json

from models.match import Match
from models.prediction import ExpertPrediction as Prediction


class PrecisionJournal:
    """
    Service pour vérifier la précision des prédictions après les matchs.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def verify_yesterday_predictions(self) -> Dict:
        """
        Vérifie les prédictions des matchs d'hier.
        
        Returns:
            Dict avec les statistiques de précision
        """
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_start = yesterday.replace(hour=0, minute=0, second=0)
        yesterday_end = yesterday.replace(hour=23, minute=59, second=59)
        
        # Récupérer les matchs terminés d'hier
        matches = self.db.query(Match).filter(
            and_(
                Match.match_date >= yesterday_start,
                Match.match_date <= yesterday_end,
                Match.status == 'FINISHED'
            )
        ).all()
        
        results = {
            'date': yesterday.strftime('%Y-%m-%d'),
            'total_matches': len(matches),
            'predictions_checked': 0,
            'correct_winner': 0,
            'correct_score': 0,
            'correct_goals_over_under': 0,
            'details': []
        }
        
        for match in matches:
            if not match.prediction:
                continue
            
            pred = match.prediction
            results['predictions_checked'] += 1
            
            # Vérifier le vainqueur prédit
            predicted_winner = self._get_predicted_winner(pred)
            actual_winner = self._get_actual_winner(match)
            winner_correct = predicted_winner == actual_winner
            
            if winner_correct:
                results['correct_winner'] += 1
            
            # Vérifier le score exact
            score_correct = (
                pred.home_score_forecast == match.score_home and
                pred.away_score_forecast == match.score_away
            )
            if score_correct:
                results['correct_score'] += 1
            
            # Vérifier Over/Under 2.5
            predicted_total = pred.home_score_forecast + pred.away_score_forecast
            actual_total = (match.score_home or 0) + (match.score_away or 0)
            over_under_correct = (predicted_total > 2.5) == (actual_total > 2.5)
            
            if over_under_correct:
                results['correct_goals_over_under'] += 1
            
            # Détail du match
            results['details'].append({
                'match_id': match.id,
                'teams': f"{match.home_team} vs {match.away_team}",
                'predicted_score': f"{pred.home_score_forecast}-{pred.away_score_forecast}",
                'actual_score': f"{match.score_home}-{match.score_away}",
                'winner_correct': winner_correct,
                'score_correct': score_correct,
                'over_under_correct': over_under_correct,
                'prediction_confidence': pred.confidence
            })
            
            # Mettre à jour le statut de la prédiction
            pred.verified = True
            pred.winner_correct = winner_correct
            pred.score_correct = score_correct
        
        self.db.commit()
        
        # Calculer les pourcentages
        if results['predictions_checked'] > 0:
            results['winner_accuracy'] = round(
                results['correct_winner'] / results['predictions_checked'] * 100, 1
            )
            results['score_accuracy'] = round(
                results['correct_score'] / results['predictions_checked'] * 100, 1
            )
            results['over_under_accuracy'] = round(
                results['correct_goals_over_under'] / results['predictions_checked'] * 100, 1
            )
        else:
            results['winner_accuracy'] = 0
            results['score_accuracy'] = 0
            results['over_under_accuracy'] = 0
        
        return results
    
    def get_overall_stats(self, days: int = 30) -> Dict:
        """
        Récupère les statistiques globales sur les N derniers jours.
        
        Args:
            days: Nombre de jours à analyser
            
        Returns:
            Dict avec les statistiques globales
        """
        start_date = datetime.now() - timedelta(days=days)
        
        # Récupérer toutes les prédictions vérifiées
        predictions = self.db.query(Prediction).join(Match).filter(
            and_(
                Match.match_date >= start_date,
                Match.status == 'FINISHED',
                Prediction.verified == True
            )
        ).all()
        
        if not predictions:
            return {
                'period': f'{days} derniers jours',
                'total_predictions': 0,
                'winner_accuracy': 0,
                'score_accuracy': 0,
                'average_confidence': 0
            }
        
        total = len(predictions)
        winner_correct = sum(1 for p in predictions if p.winner_correct)
        score_correct = sum(1 for p in predictions if p.score_correct)
        avg_confidence = sum(p.confidence or 0 for p in predictions) / total
        
        return {
            'period': f'{days} derniers jours',
            'total_predictions': total,
            'winner_accuracy': round(winner_correct / total * 100, 1),
            'score_accuracy': round(score_correct / total * 100, 1),
            'average_confidence': round(avg_confidence * 100, 1),
            'calibration': self._calculate_calibration(predictions)
        }
    
    def _get_predicted_winner(self, pred: Prediction) -> str:
        """Détermine le vainqueur prédit."""
        if pred.home_score_forecast > pred.away_score_forecast:
            return 'home'
        elif pred.away_score_forecast > pred.home_score_forecast:
            return 'away'
        return 'draw'
    
    def _get_actual_winner(self, match: Match) -> str:
        """Détermine le vainqueur réel."""
        if (match.score_home or 0) > (match.score_away or 0):
            return 'home'
        elif (match.score_away or 0) > (match.score_home or 0):
            return 'away'
        return 'draw'
    
    def _calculate_calibration(self, predictions: List[Prediction]) -> Dict:
        """
        Calcule la calibration du modèle.
        
        Une bonne calibration signifie que quand on prédit 70% de confiance,
        on a ~70% de réussite.
        """
        bins = {
            '0-40': {'total': 0, 'correct': 0},
            '40-60': {'total': 0, 'correct': 0},
            '60-80': {'total': 0, 'correct': 0},
            '80-100': {'total': 0, 'correct': 0}
        }
        
        for pred in predictions:
            conf = (pred.confidence or 0) * 100
            
            if conf < 40:
                bin_key = '0-40'
            elif conf < 60:
                bin_key = '40-60'
            elif conf < 80:
                bin_key = '60-80'
            else:
                bin_key = '80-100'
            
            bins[bin_key]['total'] += 1
            if pred.winner_correct:
                bins[bin_key]['correct'] += 1
        
        # Calculer le taux de réussite par bin
        calibration = {}
        for bin_key, data in bins.items():
            if data['total'] > 0:
                calibration[bin_key] = {
                    'matches': data['total'],
                    'accuracy': round(data['correct'] / data['total'] * 100, 1)
                }
            else:
                calibration[bin_key] = {'matches': 0, 'accuracy': None}
        
        return calibration


# Fonction pour créer une tâche quotidienne
async def daily_verification_task(db: Session):
    """
    Tâche quotidienne pour vérifier les prédictions d'hier.
    À appeler chaque matin via un scheduler (comme Celery ou APScheduler).
    """
    journal = PrecisionJournal(db)
    results = await journal.verify_yesterday_predictions()
    
    print(f"📊 Journal de Précision - {results['date']}")
    print(f"   Total matchs vérifiés: {results['predictions_checked']}")
    print(f"   Vainqueurs corrects: {results['correct_winner']} ({results['winner_accuracy']}%)")
    print(f"   Scores exacts: {results['correct_score']} ({results['score_accuracy']}%)")
    print(f"   Over/Under 2.5: {results['correct_goals_over_under']} ({results['over_under_accuracy']}%)")
    
    return results
