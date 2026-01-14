"""
Tests pour le service de prédiction multi-logique.

Ce fichier teste les 3 logiques de prédiction:
- Logique de Papa (35%)
- Logique de Grand Frère (35%)
- Ma Logique (30%)
"""
import pytest
from fastapi import status


class TestCombinedPredictionEndpoint:
    """Tests pour l'endpoint /matches/{id}/prediction/combined."""
    
    def test_combined_prediction_valid_match(self, client, db_session):
        """Test: Prédiction combinée pour un match valide avec données."""
        # D'abord, récupérer un match existant
        matches_response = client.get("/api/v1/matches?limit=1")
        
        if matches_response.status_code == 200:
            data = matches_response.json()
            if data["count"] > 0:
                match_id = data["matches"][0]["id"]
                
                # Tester l'endpoint de prédiction combinée
                response = client.get(f"/api/v1/matches/{match_id}/prediction/combined")
                
                # 200 si données suffisantes, 422 sinon
                assert response.status_code in [200, 422]
                
                if response.status_code == 200:
                    pred = response.json()
                    # Vérifier la structure
                    assert "match_id" in pred
                    assert "final_home_goals" in pred
                    assert "final_away_goals" in pred
                    assert "final_confidence" in pred
                    assert "consensus_level" in pred
                    assert pred["consensus_level"] in ["FORT", "MOYEN", "FAIBLE"]
    
    def test_combined_prediction_invalid_match(self, client):
        """Test: 404 pour un match inexistant."""
        response = client.get("/api/v1/matches/99999/prediction/combined")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_combined_prediction_structure(self, client):
        """Test: Structure de la réponse de prédiction combinée."""
        matches_response = client.get("/api/v1/matches?limit=5")
        
        if matches_response.status_code == 200:
            data = matches_response.json()
            for match in data.get("matches", []):
                match_id = match["id"]
                response = client.get(f"/api/v1/matches/{match_id}/prediction/combined")
                
                if response.status_code == 200:
                    pred = response.json()
                    
                    # Vérifier les champs de base
                    assert isinstance(pred["final_home_goals"], int)
                    assert isinstance(pred["final_away_goals"], int)
                    assert 0 <= pred["final_confidence"] <= 1
                    assert isinstance(pred["all_agree"], bool)
                    
                    # Vérifier les prédictions par logique (peuvent être null)
                    for logic_key in ["papa_prediction", "grand_frere_prediction", "ma_logique_prediction"]:
                        if pred.get(logic_key):
                            logic = pred[logic_key]
                            assert "home_win_prob" in logic
                            assert "draw_prob" in logic
                            assert "away_win_prob" in logic
                            assert "bet_tip" in logic
                            assert "analysis" in logic
                    break  # Un seul test suffit


class TestMatchesEndpoints:
    """Tests complets pour les endpoints matches."""
    
    def test_get_matches_pagination(self, client):
        """Test: Pagination des matchs."""
        # Test limit
        response = client.get("/api/v1/matches?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["matches"]) <= 5
        
        # Test offset
        response2 = client.get("/api/v1/matches?limit=5&offset=5")
        assert response2.status_code == 200
    
    def test_get_matches_by_competition(self, client):
        """Test: Filtrage par compétition."""
        response = client.get("/api/v1/matches?competition=PL")
        assert response.status_code == 200
        data = response.json()
        for match in data.get("matches", []):
            assert match["competition_code"] == "PL"
    
    def test_get_single_match(self, client):
        """Test: Récupération d'un match unique."""
        # D'abord, obtenir un ID de match valide
        list_response = client.get("/api/v1/matches?limit=1")
        if list_response.status_code == 200 and list_response.json()["count"] > 0:
            match_id = list_response.json()["matches"][0]["id"]
            
            response = client.get(f"/api/v1/matches/{match_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == match_id
            assert "home_team" in data
            assert "away_team" in data
    
    def test_get_match_not_found(self, client):
        """Test: 404 pour match inexistant."""
        response = client.get("/api/v1/matches/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestStandingsEndpoints:
    """Tests pour les endpoints standings."""
    
    def test_get_standings_pl(self, client):
        """Test: Classement Premier League."""
        response = client.get("/api/v1/matches/competitions/PL/standings")
        assert response.status_code == 200
        data = response.json()
        assert "standings" in data
        assert data["competition_code"] == "PL"
    
    def test_get_standings_bundesliga(self, client):
        """Test: Classement Bundesliga."""
        response = client.get("/api/v1/matches/competitions/BL1/standings")
        assert response.status_code == 200
        data = response.json()
        assert "standings" in data
    
    def test_get_standings_invalid_competition(self, client):
        """Test: Compétition invalide."""
        response = client.get("/api/v1/matches/competitions/INVALID/standings")
        # 200 (liste vide), 404, ou 502 (API externe error)
        assert response.status_code in [200, 404, 502]


class TestTeamStatsEndpoint:
    """Tests pour les endpoints team stats."""
    
    def test_get_team_stats_with_competition(self, client):
        """Test: Stats d'équipe avec paramètre competition requis."""
        # D'abord, récupérer une équipe depuis les standings
        standings_response = client.get("/api/v1/matches/competitions/PL/standings")
        
        if standings_response.status_code == 200:
            standings = standings_response.json().get("standings", [])
            if standings:
                team_id = standings[0]["team_id"]
                
                response = client.get(f"/api/v1/teams/{team_id}/stats?competition=PL")
                # 200 si stats existent, 404 sinon
                assert response.status_code in [200, 404]
    
    def test_get_team_stats_missing_competition(self, client):
        """Test: 422 si paramètre competition manquant."""
        response = client.get("/api/v1/teams/1/stats")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCompetitionsEndpoint:
    """Tests pour les endpoints competitions."""
    
    def test_get_competitions_list(self, client):
        """Test: Liste des compétitions."""
        response = client.get("/api/v1/matches/competitions")
        # 200 ou 502 si API externe down
        assert response.status_code in [200, 502]
        
        if response.status_code == 200:
            data = response.json()
            assert "competitions" in data


class TestH2HEndpoint:
    """Tests pour l'endpoint H2H."""
    
    def test_get_h2h_for_match(self, client):
        """Test: H2H pour un match."""
        # Récupérer un match
        matches_response = client.get("/api/v1/matches?limit=1")
        
        if matches_response.status_code == 200 and matches_response.json()["count"] > 0:
            match_id = matches_response.json()["matches"][0]["id"]
            
            response = client.get(f"/api/v1/matches/{match_id}/h2h")
            # 200 si H2H disponible, 404 ou 502 sinon
            assert response.status_code in [200, 404, 502]
    
    def test_get_h2h_invalid_match(self, client):
        """Test: 404 pour match inexistant."""
        response = client.get("/api/v1/matches/99999/h2h")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPredictionEndpoint:
    """Tests pour l'endpoint prediction standard."""
    
    def test_get_prediction_for_match(self, client):
        """Test: Prédiction pour un match."""
        matches_response = client.get("/api/v1/matches?limit=1")
        
        if matches_response.status_code == 200 and matches_response.json()["count"] > 0:
            match_id = matches_response.json()["matches"][0]["id"]
            
            response = client.get(f"/api/v1/matches/{match_id}/prediction")
            # 200 si prédiction existe, 404 sinon
            assert response.status_code in [200, 404]
