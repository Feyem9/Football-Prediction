"""
Controller pour les matchs, compétitions et prédictions.

Contient toute la logique métier pour les endpoints matches.
"""
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException

from models.match import Match
from models.prediction import ExpertPrediction
from schemas.match import (
    MatchResponse,
    MatchListResponse,
    CompetitionResponse,
    CompetitionListResponse,
    StandingsResponse,
    StandingEntry,
    PredictionSummary,
    PredictionResponse,
    CombinedPredictionResponse,
    LogicPredictionResult,
    LogicEvidenceSchema
)
from services.football_api import football_data_service, FootballDataService
from services.match_sync import MatchSyncService
from services.prediction_service import PredictionService
from services.multi_logic_engine import MultiLogicPredictionEngine
from schemas.h2h import H2HResponse


# =====================
# Helpers
# =====================

def match_to_response(match: Match) -> MatchResponse:
    """Convertit un Match en MatchResponse avec prédiction."""
    prediction = None
    if match.expert_prediction:
        pred = match.expert_prediction
        prediction = PredictionSummary(
            # Score final (consensus)
            home_score_forecast=pred.home_score_forecast,
            away_score_forecast=pred.away_score_forecast,
            confidence=pred.confidence,
            bet_tip=pred.bet_tip,
            home_goals_avg=getattr(pred, 'home_goals_avg', None),
            away_goals_avg=getattr(pred, 'away_goals_avg', None),
            # Logique de Papa
            papa_home_score=getattr(pred, 'papa_home_score', None),
            papa_away_score=getattr(pred, 'papa_away_score', None),
            papa_confidence=getattr(pred, 'papa_confidence', None),
            papa_tip=getattr(pred, 'papa_tip', None),
            # Logique Grand Frère
            grand_frere_home_score=getattr(pred, 'grand_frere_home_score', None),
            grand_frere_away_score=getattr(pred, 'grand_frere_away_score', None),
            grand_frere_confidence=getattr(pred, 'grand_frere_confidence', None),
            grand_frere_tip=getattr(pred, 'grand_frere_tip', None),
            # Ma Logique
            ma_logique_home_score=getattr(pred, 'ma_logique_home_score', None),
            ma_logique_away_score=getattr(pred, 'ma_logique_away_score', None),
            ma_logique_confidence=getattr(pred, 'ma_logique_confidence', None),
            ma_logique_tip=getattr(pred, 'ma_logique_tip', None)
        )
    
    return MatchResponse(
        id=match.id,
        external_id=match.external_id,
        competition_code=match.competition_code,
        competition_name=match.competition_name,
        matchday=match.matchday,
        home_team=match.home_team,
        home_team_short=match.home_team_short,
        home_team_crest=match.home_team_crest,
        away_team=match.away_team,
        away_team_short=match.away_team_short,
        away_team_crest=match.away_team_crest,
        match_date=match.match_date,
        status=match.status,
        score_home=match.score_home,
        score_away=match.score_away,
        prediction=prediction
    )


# =====================
# Match Controllers
# =====================

def get_matches(
    db: Session,
    competition: Optional[str] = None,
    status: Optional[str] = None,
    date: Optional[str] = None,
    limit: int = 20
) -> MatchListResponse:
    """Récupère la liste des matchs avec filtres."""
    # Optimisation: joinedload pour éviter N+1 sur 'expert_prediction'
    query = db.query(Match).options(joinedload(Match.expert_prediction))
    
    if competition:
        query = query.filter(Match.competition_code == competition.upper())
    
    if status:
        query = query.filter(Match.status == status.upper())
    
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
            start = target_date.replace(hour=0, minute=0, second=0)
            end = start + timedelta(days=1)
            query = query.filter(Match.match_date >= start, Match.match_date < end)
        except ValueError:
            raise HTTPException(status_code=400, detail="Format date invalide. Utilisez YYYY-MM-DD")
    else:
        # Par défaut: matchs des 7 derniers jours + 30 prochains jours
        now = datetime.now()
        date_from = now - timedelta(days=7)
        date_to = now + timedelta(days=30)
        query = query.filter(Match.match_date >= date_from, Match.match_date <= date_to)
    
    # Trier par date décroissante (matchs récents/à venir en premier)
    matches = query.order_by(Match.match_date.desc()).limit(limit).all()
    match_responses = [match_to_response(m) for m in matches]
    
    return MatchListResponse(count=len(match_responses), matches=match_responses)


def get_upcoming_matches(db: Session, limit: int = 20) -> MatchListResponse:
    """Récupère les prochains matchs programmés."""
    sync_service = MatchSyncService(db)
    matches = sync_service.get_upcoming_matches(limit=limit)
    match_responses = [match_to_response(m) for m in matches]
    
    return MatchListResponse(count=len(match_responses), matches=match_responses)


def get_today_matches(db: Session) -> MatchListResponse:
    """Récupère les matchs du jour."""
    sync_service = MatchSyncService(db)
    matches = sync_service.get_matches_by_date()
    match_responses = [match_to_response(m) for m in matches]
    
    return MatchListResponse(count=len(match_responses), matches=match_responses)


def get_match_by_id(db: Session, match_id: int) -> MatchResponse:
    """Récupère un match par son ID."""
    # Optimisation: joinedload
    match = db.query(Match).options(joinedload(Match.expert_prediction)).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match non trouvé")
    
    return match_to_response(match)


async def get_match_prediction(db: Session, match_id: int) -> PredictionResponse:
    """Récupère ou génère la prédiction d'un match."""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match non trouvé")
    
    prediction_service = PredictionService(db)
    prediction = await prediction_service.generate_prediction(match)
    
    if not prediction:
        raise HTTPException(status_code=500, detail="Impossible de générer la prédiction")
    
    return prediction


# =====================
# Competition Controllers
# =====================

async def get_competitions() -> CompetitionListResponse:
    """Liste toutes les compétitions disponibles."""
    try:
        result = await football_data_service.get_competitions()
        competitions = result.get("competitions", [])
        
        competition_list = []
        for comp in competitions:
            code = comp.get("code")
            if code in FootballDataService.TIER_ONE_COMPETITIONS:
                competition_list.append(CompetitionResponse(
                    id=comp.get("id"),
                    code=code,
                    name=comp.get("name"),
                    area=comp.get("area", {}).get("name", ""),
                    emblem=comp.get("emblem"),
                    type=comp.get("type"),
                    current_season=comp.get("currentSeason", {}).get("id"),
                    current_matchday=comp.get("currentSeason", {}).get("currentMatchday")
                ))
        
        return CompetitionListResponse(count=len(competition_list), competitions=competition_list)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erreur API externe: {str(e)}")


async def get_competition(code: str) -> CompetitionResponse:
    """Détails d'une compétition spécifique."""
    try:
        comp = await football_data_service.get_competition(code.upper())
        
        return CompetitionResponse(
            id=comp.get("id"),
            code=comp.get("code"),
            name=comp.get("name"),
            area=comp.get("area", {}).get("name", ""),
            emblem=comp.get("emblem"),
            type=comp.get("type"),
            current_season=comp.get("currentSeason", {}).get("id"),
            current_matchday=comp.get("currentSeason", {}).get("currentMatchday")
        )
    except Exception:
        raise HTTPException(status_code=404, detail=f"Compétition non trouvée: {code}")


async def get_standings(code: str) -> StandingsResponse:
    """Récupère le classement d'une compétition."""
    try:
        result = await football_data_service.get_standings(code.upper())
        
        standings_data = result.get("standings", [])
        if not standings_data:
            raise HTTPException(status_code=404, detail="Classement non disponible")
        
        table = standings_data[0].get("table", [])
        
        standings = []
        for entry in table:
            team = entry.get("team", {})
            standings.append(StandingEntry(
                position=entry.get("position"),
                team_id=team.get("id"),
                team_name=team.get("name"),
                team_short=team.get("shortName") or team.get("tla"),
                team_crest=team.get("crest"),
                played_games=entry.get("playedGames", 0),
                won=entry.get("won", 0),
                draw=entry.get("draw", 0),
                lost=entry.get("lost", 0),
                points=entry.get("points", 0),
                goals_for=entry.get("goalsFor", 0),
                goals_against=entry.get("goalsAgainst", 0),
                goal_difference=entry.get("goalDifference", 0),
                form=entry.get("form")
            ))
        
        return StandingsResponse(
            competition_code=result.get("competition", {}).get("code", code.upper()),
            competition_name=result.get("competition", {}).get("name", ""),
            season=result.get("season", {}).get("id", 0),
            matchday=result.get("season", {}).get("currentMatchday"),
            standings=standings
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erreur API: {str(e)}")


# =====================
# Sync Controllers
# =====================

async def sync_matches(db: Session, competition: Optional[str] = None) -> dict:
    """Synchronise les matchs depuis Football-Data.org."""
    sync_service = MatchSyncService(db)
    
    try:
        if competition:
            count = await sync_service.sync_competition_matches(competition.upper())
            return {"message": f"{count} matchs synchronisés pour {competition.upper()}"}
        else:
            count = await sync_service.sync_upcoming_matches(days=7)
            return {"message": f"{count} matchs synchronisés"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de synchronisation: {str(e)}")


async def generate_predictions(db: Session, limit: int = 20, force: bool = False) -> dict:
    """Génère des prédictions pour les matchs à venir."""
    prediction_service = PredictionService(db)
    
    try:
        # Si force=True, supprimer les prédictions existantes
        if force:
            from models.prediction import ExpertPrediction
            deleted = db.query(ExpertPrediction).delete()
            db.commit()
            logger.info(f"🗑️ {deleted} prédictions supprimées (force=True)")
        
        count = await prediction_service.generate_predictions_for_upcoming(limit=limit)
        msg = f"{count} prédictions générées"
        if force:
            msg += f" (après suppression de {deleted} anciennes)"
        return {"message": msg}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de génération: {str(e)}")


async def get_match_h2h(db: Session, match_id: int) -> H2HResponse:
    """Récupère le Head-to-Head pour un match."""
    # On commence par vérifier si le match existe en DB pour avoir l'ID externe
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match or not match.external_id:
        raise HTTPException(status_code=404, detail="Match non trouvé ou ID externe manquant")
    
    try:
        data = await football_data_service.get_match_h2h(match.external_id)
        return H2HResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erreur API lors de la récupération du H2H: {str(e)}")


async def get_team_matches(team_id: int, limit: int = 10) -> dict:
    """Récupère les derniers matchs d'une équipe."""
    try:
        return await football_data_service.get_team_matches(team_id, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erreur API: {str(e)}")


async def get_combined_prediction(db: Session, match_id: int) -> CombinedPredictionResponse:
    """
    Génère une prédiction combinée utilisant les 3 logiques familiales.
    
    Logiques:
    - Papa (35%): Position + Niveau championnat + Moyenne buts
    - Grand Frère (35%): H2H + Loi domicile
    - Ma Logique (30%): Forme 10 matchs + Consensus
    """
    # Récupérer le match
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match non trouvé")
    
    # Générer la prédiction combinée
    engine = MultiLogicPredictionEngine(db)
    combined = await engine.generate_combined_prediction(match)
    
    if not combined:
        raise HTTPException(
            status_code=422, 
            detail="Impossible de générer une prédiction (données insuffisantes)"
        )
    
    # Convertir les LogicResult en LogicPredictionResult
    def logic_to_response(logic_result):
        if not logic_result:
            return None
        
        # Convertir evidence dataclass en schema
        evidence_schema = None
        if logic_result.evidence:
            ev = logic_result.evidence
            evidence_schema = LogicEvidenceSchema(
                home_position=ev.home_position,
                away_position=ev.away_position,
                home_points=ev.home_points,
                away_points=ev.away_points,
                league_level=ev.league_level,
                home_advantage=ev.home_advantage,
                home_strength=ev.home_strength,
                away_strength=ev.away_strength,
                h2h_home_wins=ev.h2h_home_wins,
                h2h_away_wins=ev.h2h_away_wins,
                h2h_draws=ev.h2h_draws,
                home_form=ev.home_form,
                away_form=ev.away_form,
                home_avg_goals=ev.home_avg_goals,
                away_avg_goals=ev.away_avg_goals,
            )
        
        return LogicPredictionResult(
            home_win_prob=logic_result.home_win_prob,
            draw_prob=logic_result.draw_prob,
            away_win_prob=logic_result.away_win_prob,
            predicted_home_goals=logic_result.predicted_home_goals,
            predicted_away_goals=logic_result.predicted_away_goals,
            confidence=logic_result.confidence,
            bet_tip=logic_result.bet_tip,
            analysis=logic_result.analysis,
            evidence=evidence_schema
        )
    
    return CombinedPredictionResponse(
        match_id=match.id,
        home_team=match.home_team,
        away_team=match.away_team,
        papa_prediction=logic_to_response(combined.papa_result),
        grand_frere_prediction=logic_to_response(combined.grand_frere_result),
        ma_logique_prediction=logic_to_response(combined.ma_logique_result),
        final_home_goals=combined.final_home_goals,
        final_away_goals=combined.final_away_goals,
        final_confidence=combined.final_confidence,
        final_bet_tip=combined.final_bet_tip,
        consensus_level=combined.consensus_level,
        all_agree=combined.all_agree
    )
