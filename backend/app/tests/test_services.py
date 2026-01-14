"""
Tests unitaires pour les services de prédiction.

Ce fichier teste les fonctions individuelles des services:
- PredictionService
- MultiLogicPredictionEngine
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from services.prediction_service import PredictionService
from services.multi_logic_engine import MultiLogicPredictionEngine, LogicResult


class TestPredictionServiceUnit:
    """Tests unitaires pour PredictionService."""
    
    def test_league_strength_values(self):
        """Test: Valeurs de force des championnats."""
        ps = PredictionService(db=None)
        
        assert ps.LEAGUE_STRENGTH["PL"] == 1.0
        assert ps.LEAGUE_STRENGTH["FL1"] == 0.8
        assert ps.LEAGUE_STRENGTH["BL1"] == 0.9
    
    def test_get_league_strength_known(self):
        """Test: Force d'un championnat connu."""
        ps = PredictionService(db=None)
        
        assert ps._get_league_strength("PL") == 1.0
        assert ps._get_league_strength("SA") == 0.9
    
    def test_get_league_strength_unknown(self):
        """Test: Force d'un championnat inconnu (défaut 0.75)."""
        ps = PredictionService(db=None)
        
        assert ps._get_league_strength("UNKNOWN") == 0.75
        assert ps._get_league_strength("XXX") == 0.75
    
    def test_calculate_form_score_empty(self):
        """Test: Forme vide retourne 0.5."""
        ps = PredictionService(db=None)
        
        assert ps._calculate_form_score("") == 0.5
        assert ps._calculate_form_score(None) == 0.5
    
    def test_calculate_form_score_all_wins(self):
        """Test: Toutes victoires = score maximum."""
        ps = PredictionService(db=None)
        
        form = "W,W,W,W,W,W,W,W,W,W"  # 10 victoires
        score = ps._calculate_form_score(form, 10)
        assert score == 1.0
    
    def test_calculate_form_score_all_losses(self):
        """Test: Toutes défaites = score 0."""
        ps = PredictionService(db=None)
        
        form = "L,L,L,L,L,L,L,L,L,L"  # 10 défaites
        score = ps._calculate_form_score(form, 10)
        assert score == 0.0
    
    def test_calculate_form_score_mixed(self):
        """Test: Forme mixte."""
        ps = PredictionService(db=None)
        
        # 5W (15pts) + 3D (3pts) + 2L (0pts) = 18pts / 30 = 0.6
        form = "W,W,W,W,W,D,D,D,L,L"
        score = ps._calculate_form_score(form, 10)
        assert score == 0.6
    
    def test_calculate_home_advantage_equal_teams(self):
        """Test: Équipes égales - avantage standard."""
        ps = PredictionService(db=None)
        
        adv = ps._calculate_home_advantage(0.7, 0.7, True)
        assert adv == ps.HOME_ADVANTAGE
    
    def test_calculate_home_advantage_weak_home_vs_strong(self):
        """Test: Faible à domicile vs fort - bonus renforcé."""
        ps = PredictionService(db=None)
        
        # Domicile faible (0.5) vs extérieur fort (0.8)
        adv = ps._calculate_home_advantage(0.5, 0.8, False)
        # Devrait être renforcé (1.5x)
        assert adv == ps.HOME_ADVANTAGE * 1.5


class TestMultiLogicEngineUnit:
    """Tests unitaires pour MultiLogicPredictionEngine."""
    
    def test_weights_sum_to_one(self):
        """Test: Les poids des 3 logiques = 100%."""
        total = (
            MultiLogicPredictionEngine.WEIGHT_PAPA +
            MultiLogicPredictionEngine.WEIGHT_GRAND_FRERE +
            MultiLogicPredictionEngine.WEIGHT_MA_LOGIQUE
        )
        assert total == 1.0
    
    def test_weight_papa(self):
        """Test: Poids de Papa = 35%."""
        assert MultiLogicPredictionEngine.WEIGHT_PAPA == 0.35
    
    def test_weight_grand_frere(self):
        """Test: Poids de Grand Frère = 35%."""
        assert MultiLogicPredictionEngine.WEIGHT_GRAND_FRERE == 0.35
    
    def test_weight_ma_logique(self):
        """Test: Poids de Ma Logique = 30%."""
        assert MultiLogicPredictionEngine.WEIGHT_MA_LOGIQUE == 0.30


class TestLogicResultDataclass:
    """Tests pour le dataclass LogicResult."""
    
    def test_logic_result_creation(self):
        """Test: Création d'un LogicResult."""
        result = LogicResult(
            home_win_prob=0.5,
            draw_prob=0.3,
            away_win_prob=0.2,
            predicted_home_goals=2,
            predicted_away_goals=1,
            confidence=0.7,
            bet_tip="1 (Victoire domicile)",
            analysis="Test analysis"
        )
        
        assert result.home_win_prob == 0.5
        assert result.predicted_home_goals == 2
        assert result.confidence == 0.7
    
    def test_logic_result_probabilities_sum(self):
        """Test: Les probabilités devraient sommer à ~1."""
        result = LogicResult(
            home_win_prob=0.45,
            draw_prob=0.30,
            away_win_prob=0.25,
            predicted_home_goals=1,
            predicted_away_goals=1,
            confidence=0.6,
            bet_tip="X",
            analysis="Test"
        )
        
        total = result.home_win_prob + result.draw_prob + result.away_win_prob
        assert abs(total - 1.0) < 0.01  # Tolérance pour arrondis
