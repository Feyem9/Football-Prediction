/**
 * Types pour l'API Pronoscore
 */

export interface Match {
  id: number;
  external_id: number;
  competition_code: string;
  competition_name: string;
  matchday: number | null;
  home_team: string;
  home_team_short?: string;
  home_team_crest?: string;
  home_standing_position?: number | null;
  home_standing_points?: number | null;
  away_team: string;
  away_team_short?: string;
  away_team_crest?: string;
  away_standing_position?: number | null;
  away_standing_points?: number | null;
  score_home: number | null;  // API renvoie score_home pas home_score
  score_away: number | null;  // API renvoie score_away pas away_score
  match_date: string;
  status: 'SCHEDULED' | 'TIMED' | 'IN_PLAY' | 'PAUSED' | 'FINISHED' | 'POSTPONED' | 'CANCELLED';
  prediction?: PredictionSummary;
}

export interface PredictionSummary {
  // Score final (consensus)
  home_score_forecast: number;
  away_score_forecast: number;
  confidence: number;
  bet_tip: string;
  home_goals_avg?: number;
  away_goals_avg?: number;
  
  // Logique de Papa (Classement + Niveau Championnat)
  papa_home_score?: number;
  papa_away_score?: number;
  papa_confidence?: number;
  papa_tip?: string;
  
  // Logique Grand Frère (H2H + Domicile)
  grand_frere_home_score?: number;
  grand_frere_away_score?: number;
  grand_frere_confidence?: number;
  grand_frere_tip?: string;
  
  // Ma Logique (Forme + Consensus)
  ma_logique_home_score?: number;
  ma_logique_away_score?: number;
  ma_logique_confidence?: number;
  ma_logique_tip?: string;
}

export interface LogicEvidence {
  // Papa - classement
  home_position?: number;
  away_position?: number;
  home_points?: number;
  away_points?: number;
  league_level?: number;
  // Grand Frère - domicile & H2H
  home_advantage?: number;
  home_strength?: 'FORT' | 'MOYEN' | 'FAIBLE';
  away_strength?: 'FORT' | 'MOYEN' | 'FAIBLE';
  h2h_home_wins?: number;
  h2h_away_wins?: number;
  h2h_draws?: number;
  // Ma Logique - forme & buts
  home_form?: number;
  away_form?: number;
  home_avg_goals?: number;
  away_avg_goals?: number;
}

export interface LogicPrediction {
  home_win_prob: number;
  draw_prob: number;
  away_win_prob: number;
  predicted_home_goals: number;
  predicted_away_goals: number;
  confidence: number;
  bet_tip: string;
  analysis: string;
  evidence?: LogicEvidence;
}

export interface CombinedPrediction {
  match_id: number;
  home_team: string;
  away_team: string;
  papa_prediction: LogicPrediction | null;
  grand_frere_prediction: LogicPrediction | null;
  ma_logique_prediction: LogicPrediction | null;
  final_home_goals: number;
  final_away_goals: number;
  final_confidence: number;
  final_bet_tip: string;
  consensus_level: 'FORT' | 'MOYEN' | 'FAIBLE';
  all_agree: boolean;
}

export interface Standing {
  position: number;
  team_id: number;
  team_name: string;
  team_short: string;
  team_crest: string;
  played_games: number;
  won: number;
  draw: number;
  lost: number;
  points: number;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  form: string | null;
}

export interface Competition {
  id: number;
  code: string;
  name: string;
  area: string;
  emblem: string;
  type: string;
  current_season: number;
  current_matchday: number;
}

export interface MatchesResponse {
  count: number;
  matches: Match[];
}

export interface StandingsResponse {
  competition_code: string;
  competition_name: string;
  season: number;
  matchday: number;
  standings: Standing[];
}

export interface CompetitionsResponse {
  count: number;
  competitions: Competition[];
}
