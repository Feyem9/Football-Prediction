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
    LogicEvidenceSchema,
    Apex30FullReport,
    Apex30ModuleReport
)
from services.football_api import football_data_service, FootballDataService
from services.match_sync import MatchSyncService
from services.prediction_service import PredictionService
from services.multi_logic_engine import MultiLogicPredictionEngine
from schemas.h2h import H2HResponse


# =====================
# Helpers
# =====================

def match_to_response(match: Match, db: Session = None) -> MatchResponse:
    """Convertit un Match en MatchResponse avec prédiction et classement."""
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
            ma_logique_tip=getattr(pred, 'ma_logique_tip', None),
            # Matchs importants
            home_upcoming_important=getattr(pred, 'home_upcoming_important', None),
            home_recent_important=getattr(pred, 'home_recent_important', None),
            away_upcoming_important=getattr(pred, 'away_upcoming_important', None),
            away_recent_important=getattr(pred, 'away_recent_important', None),
            # Données pour Preuves
            h2h_home_wins=getattr(pred, 'h2h_home_wins', None),
            h2h_away_wins=getattr(pred, 'h2h_away_wins', None),
            h2h_draws=getattr(pred, 'h2h_draws', None),
            h2h_matches_count=getattr(pred, 'h2h_matches_count', None),
            h2h_home_goals_total=getattr(pred, 'h2h_home_goals_total', None),
            h2h_away_goals_total=getattr(pred, 'h2h_away_goals_total', None),
            h2h_home_goals_freq=getattr(pred, 'h2h_home_goals_freq', None),
            h2h_away_goals_freq=getattr(pred, 'h2h_away_goals_freq', None),
            h2h_top_scorer=getattr(pred, 'h2h_top_scorer', None),
            home_form_score=getattr(pred, 'home_form_score', None),
            away_form_score=getattr(pred, 'away_form_score', None),
            # Grand Frère : Analyse combinée
            gf_home_league_level=getattr(pred, 'gf_home_league_level', None),
            gf_away_league_level=getattr(pred, 'gf_away_league_level', None),
            gf_home_advantage_bonus=getattr(pred, 'gf_home_advantage_bonus', None),
            gf_verdict=getattr(pred, 'gf_verdict', None)
        )
    
    # Récupérer les données de classement si DB session fournie
    home_position, home_points = None, None
    away_position, away_points = None, None
    
    if db and match.home_team_id and match.competition_code:
        from models.standing import Standing
        
        # Seules les compétitions VRAIMENT internationales sans classement de ligue
        # CL et EL ont maintenant des classements depuis le nouveau format 2024/2025
        international_competitions = ['WC', 'EC']  # World Cup, Euro Championship
        
        if match.competition_code not in international_competitions:
            # Classement équipe domicile (prendre le plus récent)
            home_standing = db.query(Standing).filter(
                Standing.team_id == match.home_team_id,
                Standing.competition_code == match.competition_code
            ).order_by(Standing.last_synced.desc()).first()
            
            if home_standing:
                home_position = home_standing.position
                home_points = home_standing.points
            
            # Classement équipe extérieur  
            if match.away_team_id:
                away_standing = db.query(Standing).filter(
                    Standing.team_id == match.away_team_id,
                    Standing.competition_code == match.competition_code
                ).order_by(Standing.last_synced.desc()).first()
                
                if away_standing:
                    away_position = away_standing.position
                    away_points = away_standing.points
    
    return MatchResponse(
        id=match.id,
        external_id=match.external_id,
        competition_code=match.competition_code,
        competition_name=match.competition_name,
        matchday=match.matchday,
        home_team=match.home_team,
        home_team_short=match.home_team_short,
        home_team_crest=match.home_team_crest,
        home_standing_position=home_position,
        home_standing_points=home_points,
        away_team=match.away_team,
        away_team_short=match.away_team_short,
        away_team_crest=match.away_team_crest,
        away_standing_position=away_position,
        away_standing_points=away_points,
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
    match_responses = [match_to_response(m, db) for m in matches]
    
    return MatchListResponse(count=len(match_responses), matches=match_responses)


def get_upcoming_matches(db: Session, limit: int = 20) -> MatchListResponse:
    """Récupère les prochains matchs programmés."""
    sync_service = MatchSyncService(db)
    matches = sync_service.get_upcoming_matches(limit=limit)
    match_responses = [match_to_response(m, db) for m in matches]
    
    return MatchListResponse(count=len(match_responses), matches=match_responses)


def get_today_matches(db: Session) -> MatchListResponse:
    """Récupère les matchs du jour."""
    sync_service = MatchSyncService(db)
    matches = sync_service.get_matches_by_date()
    match_responses = [match_to_response(m, db) for m in matches]
    
    return MatchListResponse(count=len(match_responses), matches=match_responses)


def get_historical_matches(db: Session, date: Optional[str] = None, competition: Optional[str] = None):
    """
    Récupère l'historique des matchs terminés avec comparaison prédiction vs résultat.
    
    Args:
        db: Session de base de données
        date: Date au format YYYY-MM-DD (défaut: hier)
        competition: Code de la compétition (optionnel)
    
    Returns:
        Matchs terminés avec prédictions et statistiques de réussite
    """
    from models.standing import Standing
    
    # Date par défaut = hier
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Format de date invalide. Utilisez YYYY-MM-DD")
    else:
        target_date = (datetime.now(timezone.utc) - timedelta(days=1)).date()
    
    # Récupérer les matchs terminés du jour
    query = db.query(Match).options(joinedload(Match.expert_prediction)).filter(
        Match.status == "FINISHED"
    )
    
    # Filtrer par date
    start_of_day = datetime.combine(target_date, datetime.min.time())
    end_of_day = datetime.combine(target_date, datetime.max.time())
    query = query.filter(Match.match_date >= start_of_day, Match.match_date <= end_of_day)
    
    # Filtrer par compétition si spécifié
    if competition:
        query = query.filter(Match.competition_code == competition)
    
    matches = query.order_by(Match.match_date).all()
    
    # Construire la réponse avec comparaison prédiction/résultat
    results = []
    stats = {
        "total": 0,
        "correct_winner": 0,
        "correct_score": 0,
        "correct_goals": 0,
        "by_competition": {}
    }
    
    for match in matches:
        pred = match.expert_prediction
        actual_home = match.score_home
        actual_away = match.score_away
        
        # Résultat réel
        if actual_home is not None and actual_away is not None:
            if actual_home > actual_away:
                actual_winner = "home"
            elif actual_away > actual_home:
                actual_winner = "away"
            else:
                actual_winner = "draw"
            actual_goals = actual_home + actual_away
        else:
            actual_winner = None
            actual_goals = None
        
        # Prédiction
        pred_winner = None
        pred_goals = None
        winner_correct = False
        score_correct = False
        goals_correct = False
        
        if pred:
            h = pred.home_score_forecast or 0
            a = pred.away_score_forecast or 0
            if h > a:
                pred_winner = "home"
            elif a > h:
                pred_winner = "away"
            else:
                pred_winner = "draw"
            pred_goals = h + a
            
            # Vérifier la réussite
            if actual_winner:
                winner_correct = pred_winner == actual_winner
                score_correct = (h == actual_home and a == actual_away)
                goals_correct = (pred_goals > 2.5) == (actual_goals > 2.5) if actual_goals is not None else False
                
                stats["total"] += 1
                if winner_correct:
                    stats["correct_winner"] += 1
                if score_correct:
                    stats["correct_score"] += 1
                if goals_correct:
                    stats["correct_goals"] += 1
                
                # Stats par compétition
                comp = match.competition_code
                if comp not in stats["by_competition"]:
                    stats["by_competition"][comp] = {"total": 0, "correct": 0, "name": match.competition_name}
                stats["by_competition"][comp]["total"] += 1
                if winner_correct:
                    stats["by_competition"][comp]["correct"] += 1
        
        results.append({
            "id": match.id,
            "competition_code": match.competition_code,
            "competition_name": match.competition_name,
            "home_team": match.home_team,
            "home_team_short": match.home_team_short,
            "home_team_crest": match.home_team_crest,
            "away_team": match.away_team,
            "away_team_short": match.away_team_short,
            "away_team_crest": match.away_team_crest,
            "match_date": match.match_date.isoformat() if match.match_date else None,
            "actual": {
                "home": actual_home,
                "away": actual_away,
                "winner": actual_winner
            },
            "prediction": {
                "home": pred.home_score_forecast if pred else None,
                "away": pred.away_score_forecast if pred else None,
                "confidence": pred.confidence if pred else None,
                "tip": pred.bet_tip if pred else None,
                "winner": pred_winner
            } if pred else None,
            "success": {
                "winner": winner_correct,
                "score": score_correct,
                "goals": goals_correct
            } if pred and actual_winner else None
        })
    
    # Calculer les pourcentages
    success_rates = {}
    if stats["total"] > 0:
        success_rates = {
            "winner": round(stats["correct_winner"] / stats["total"] * 100, 1),
            "score": round(stats["correct_score"] / stats["total"] * 100, 1),
            "goals": round(stats["correct_goals"] / stats["total"] * 100, 1)
        }
    
    return {
        "date": target_date.isoformat(),
        "count": len(results),
        "matches": results,
        "stats": {
            "total": stats["total"],
            "correct_winner": stats["correct_winner"],
            "correct_score": stats["correct_score"],
            "correct_goals": stats["correct_goals"],
            "success_rates": success_rates,
            "by_competition": stats["by_competition"]
        }
    }


def get_match_by_id(db: Session, match_id: int) -> MatchResponse:
    """Récupère un match par son ID."""
    # Optimisation: joinedload
    match = db.query(Match).options(joinedload(Match.expert_prediction)).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match non trouvé")
    
    return match_to_response(match, db)


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


async def get_apex30_report(db: Session, match_id: int) -> Apex30FullReport:
    """Récupère le rapport détaillé APEX-30 pour un match."""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match non trouvé")
    
    # Récupérer la prédiction associée
    prediction = db.query(ExpertPrediction).filter(ExpertPrediction.match_id == match_id).first()
    
    # Si la prédiction n'existe pas ou si l'analyse APEX-30 est manquante (vieille prédiction en base)
    if not prediction or not prediction.ma_logique_analysis:
        from services.prediction_service import PredictionService
        prediction_service = PredictionService(db)
        # Forcer la génération ou mise à jour pour avoir les données APEX-30
        try:
            # On supprime l'ancienne prédiction sans analyse pour forcer la regénération
            if prediction:
                db.delete(prediction)
                db.commit()
            
            prediction = await prediction_service.generate_prediction(match)
        except Exception as e:
            print(f"Erreur lors de la regénération auto de la prédiction: {e}")
    
    if not prediction or not prediction.ma_logique_analysis:
        raise HTTPException(status_code=404, detail="Analyse APEX-30 non disponible pour ce match malgré une tentative de génération.")
    
    import json
    from services.apex30_service import APEX30Service
    
    try:
        analysis_data = json.loads(prediction.ma_logique_analysis)
        apex30 = APEX30Service(db)
        
        modules = apex30.generer_rapport_detaille(
            analysis_data, 
            match.home_team, 
            match.away_team
        )
        
        summary = (
            f"Analyse APEX-30 pour {match.home_team} vs {match.away_team}. "
            f"Basée sur 8 modules pondérés. Confiance: {int(prediction.ma_logique_confidence * 100)}%."
        )
        
        return Apex30FullReport(
            match_id=match_id,
            home_team=match.home_team,
            away_team=match.away_team,
            modules=[Apex30ModuleReport(**m) for m in modules],
            summary=summary
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération du rapport: {str(e)}")


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
