"""
Routes API pour le Journal de Précision
Permet de vérifier les prédictions et afficher les statistiques de précision
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from services.precision_journal import PrecisionJournal


router = APIRouter(prefix="/precision", tags=["Precision Journal"])


@router.get("/verify/yesterday")
async def verify_yesterday(db: Session = Depends(get_db)):
    """
    Vérifie les prédictions des matchs d'hier.
    À appeler manuellement ou via un cron job.
    """
    journal = PrecisionJournal(db)
    results = await journal.verify_yesterday_predictions()
    return results


@router.get("/stats")
async def get_precision_stats(days: Optional[int] = 30, db: Session = Depends(get_db)):
    """
    Récupère les statistiques de précision sur les N derniers jours.
    
    Args:
        days: Nombre de jours à analyser (défaut: 30)
    """
    journal = PrecisionJournal(db)
    stats = journal.get_overall_stats(days=days)
    return stats


@router.get("/calibration")
async def get_calibration(days: Optional[int] = 30, db: Session = Depends(get_db)):
    """
    Récupère les données de calibration du modèle.
    Montre si la confiance prédite correspond à la précision réelle.
    """
    journal = PrecisionJournal(db)
    stats = journal.get_overall_stats(days=days)
    return {
        'calibration': stats.get('calibration', {}),
        'period': stats.get('period', f'{days} jours')
    }
