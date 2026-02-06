/**
 * Client API pour Pronoscore Backend
 */
import axios from 'axios';
import type { 
  MatchesResponse, 
  StandingsResponse, 
  CompetitionsResponse,
  CombinedPrediction,
  Match,
  Apex30FullReport,
  OddsResponse,
  ValueBetResponse
} from '../types';

// URL de l'API (production Render ou local)
const API_BASE = import.meta.env.VITE_API_URL || 'https://football-prediction-mbil.onrender.com';

const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 secondes pour gérer le cold start de Render
});

/**
 * Récupère les matchs à venir (inclut aujourd'hui)
 */
export async function getMatches(params?: {
  competition?: string;
  limit?: number;
}): Promise<MatchesResponse> {
  // Utiliser l'endpoint upcoming pour avoir les matchs actuels
  const { data } = await api.get<MatchesResponse>('/matches/upcoming', { 
    params: { limit: params?.limit || 20 }
  });
  
  // Filtrer par compétition côté client si nécessaire
  if (params && params.competition) {
    const competitionCode = params.competition.toUpperCase();
    const filtered = data.matches.filter(
      m => m.competition_code === competitionCode
    );
    return { count: filtered.length, matches: filtered };
  }
  
  return data;
}

/**
 * Récupère les matchs du jour
 */
export async function getTodayMatches(): Promise<MatchesResponse> {
  const { data } = await api.get<MatchesResponse>('/matches/today');
  return data;
}

/**
 * Récupère un match par ID
 */
export async function getMatch(matchId: number): Promise<Match> {
  const { data } = await api.get<Match>(`/matches/${matchId}`);
  return data;
}

/**
 * Récupère la prédiction combinée (3 logiques)
 */
export async function getCombinedPrediction(matchId: number): Promise<CombinedPrediction> {
  const { data } = await api.get<CombinedPrediction>(`/matches/${matchId}/prediction/combined`);
  return data;
}

/**
 * Récupère le rapport détaillé APEX-30 (8 modules)
 */
export async function getApex30Report(matchId: number): Promise<Apex30FullReport> {
  const { data } = await api.get<Apex30FullReport>(`/matches/${matchId}/apex30-report`);
  return data;
}

/**
 * Récupère les classements d'une compétition
 */
export async function getStandings(competitionCode: string): Promise<StandingsResponse> {
  const { data } = await api.get<StandingsResponse>(`/matches/competitions/${competitionCode}/standings`);
  return data;
}

/**
 * Récupère la liste des compétitions
 */
export async function getCompetitions(): Promise<CompetitionsResponse> {
  const { data } = await api.get<CompetitionsResponse>('/matches/competitions');
  return data;
}

/**
 * Vérifie l'état de santé de l'API
 */
export async function healthCheck(): Promise<{ status: string; database: string }> {
  const { data } = await api.get('/health');
  return data;
}

/**
 * Récupère les cotes d'un match
 */
export async function getOdds(matchId: number): Promise<OddsResponse> {
    const { data } = await api.get<OddsResponse>(`/odds/${matchId}`);
    return data;
}

/**
 * Force le rafraîchissement des cotes d'un match
 */
export async function refreshMatchOdds(matchId: number): Promise<OddsResponse> {
    const { data } = await api.post<OddsResponse>(`/odds/${matchId}/refresh`);
    return data;
}

/**
 * Analyse un value bet pour un type de pari
 */
export async function getValueBet(matchId: number, betType: 'home' | 'draw' | 'away'): Promise<ValueBetResponse> {
    const { data } = await api.get<ValueBetResponse>(`/odds/${matchId}/value-bet`, {
        params: { bet_type: betType }
    });
    return data;
}

export default api;
