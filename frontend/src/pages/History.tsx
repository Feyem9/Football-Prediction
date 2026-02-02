/**
 * History Page - Historique des Matchs
 * Affiche les matchs terminés avec prédiction vs résultat
 * Design premium avec navigation par date
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import type { Match } from '../types';

// Types pour l'API /history
interface HistoryMatchRaw {
  id: number;
  competition_code: string;
  competition_name: string;
  home_team: string;
  home_team_short: string;
  home_team_crest: string;
  away_team: string;
  away_team_short: string;
  away_team_crest: string;
  match_date: string;
  actual: { home: number; away: number; winner: string } | null;
  prediction: { home: number; away: number; confidence: number; tip: string; winner: string } | null;
  success: { winner: boolean; score: boolean; goals: boolean } | null;
}

interface MatchSuccess {
  winner: boolean;
  score: boolean;
  goals: boolean;
}

const API_BASE = `${import.meta.env.VITE_API_URL || 'https://football-prediction-mbil.onrender.com'}/api/v1`;

const COMP_FLAGS: Record<string, string> = {
  PL: '🏴󠁧󠁢󠁥󠁮󠁧󠁿', FL1: '🇫🇷', BL1: '🇩🇪', SA: '🇮🇹', PD: '🇪🇸', CL: '🏆', EL: '🏆',
};

export default function History() {
  const [selectedDate, setSelectedDate] = useState<string>(() => {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    return yesterday.toISOString().split('T')[0];
  });
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState({ total: 0, correct: 0, wrong: 0 });

  // Navigation par date
  const navigateDate = (days: number) => {
    const date = new Date(selectedDate);
    date.setDate(date.getDate() + days);
    // Ne pas aller dans le futur
    if (date <= new Date()) {
      setSelectedDate(date.toISOString().split('T')[0]);
    }
  };

  const formatDateDisplay = (dateStr: string) => {
    const date = new Date(dateStr + 'T12:00:00');
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    if (dateStr === today.toISOString().split('T')[0]) return "Aujourd'hui";
    if (dateStr === yesterday.toISOString().split('T')[0]) return "Hier";
    
    return date.toLocaleDateString('fr-FR', {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  useEffect(() => {
    const fetchMatches = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Utiliser le nouvel endpoint /history
        const response = await fetch(`${API_BASE}/matches/history?date=${selectedDate}`);
        if (!response.ok) throw new Error('Erreur API');
        
        const data = await response.json();
        console.log('📊 Historique reçu:', data);
        
        // Transformer les données du nouvel endpoint
        const formattedMatches: (Match & { _success?: MatchSuccess | null })[] = data.matches.map((m: HistoryMatchRaw) => ({
          id: m.id,
          competition_code: m.competition_code,
          competition_name: m.competition_name,
          home_team: m.home_team,
          home_team_short: m.home_team_short,
          home_team_crest: m.home_team_crest,
          away_team: m.away_team,
          away_team_short: m.away_team_short,
          away_team_crest: m.away_team_crest,
          match_date: m.match_date,
          score_home: m.actual?.home,
          score_away: m.actual?.away,
          prediction: m.prediction ? {
            home_score_forecast: m.prediction.home,
            away_score_forecast: m.prediction.away,
            confidence: m.prediction.confidence,
            bet_tip: m.prediction.tip
          } : null,
          _success: m.success
        }));
        
        setMatches(formattedMatches);
        
        // Stats depuis l'API
        setStats({
          total: data.stats?.total || formattedMatches.length,
          correct: data.stats?.correct_winner || 0,
          wrong: (data.stats?.total || 0) - (data.stats?.correct_winner || 0)
        });
        
      } catch (err) {
        console.error('Erreur:', err);
        setError('Impossible de charger les matchs');
      } finally {
        setLoading(false);
      }
    };
    
    fetchMatches();
  }, [selectedDate]);

  const successRate = stats.total > 0 ? Math.round((stats.correct / stats.total) * 100) : 0;

  return (
    <div className="min-h-screen pb-16">
      {/* Hero Header */}
      <div className="relative py-8 mb-6 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-900/40 via-indigo-900/30 to-blue-900/20" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-purple-500/10 via-transparent to-transparent" />
        
        <div className="relative container mx-auto px-4 text-center">
          <span className="text-5xl mb-3 block animate-pulse">📊</span>
          <h1 className="text-3xl md:text-4xl font-black text-white mb-2">
            Historique <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">des Résultats</span>
          </h1>
          <p className="text-slate-400">Analyse des prédictions passées</p>
        </div>
      </div>

      <div className="container mx-auto px-4 max-w-5xl">
        
        {/* Navigation par Date - Design premium */}
        <div className="mb-8 p-4 rounded-2xl bg-gradient-to-r from-slate-800/80 to-slate-900/80 border border-slate-700/50 backdrop-blur-xl shadow-2xl">
          <div className="flex flex-wrap items-center justify-center gap-3">
            {/* Boutons précédent */}
            <button
              onClick={() => navigateDate(-7)}
              className="px-4 py-2 rounded-xl bg-slate-700/50 hover:bg-slate-600/50 text-slate-300 hover:text-white transition-all font-medium border border-slate-600/30 hover:border-slate-500/50"
            >
              « -7j
            </button>
            <button
              onClick={() => navigateDate(-1)}
              className="px-5 py-2 rounded-xl bg-purple-900/40 hover:bg-purple-800/50 text-purple-300 hover:text-white transition-all font-bold border border-purple-500/30 hover:border-purple-400/50"
            >
              ‹ Jour précédent
            </button>
            
            {/* Date picker stylisé */}
            <div className="relative group">
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                max={new Date().toISOString().split('T')[0]}
                className="px-6 py-3 rounded-2xl bg-gradient-to-r from-indigo-900/60 to-purple-900/60 border-2 border-indigo-500/40 text-white font-bold text-center cursor-pointer hover:border-indigo-400/60 transition-all focus:outline-none focus:ring-2 focus:ring-indigo-400/50 shadow-lg shadow-indigo-900/30"
              />
              <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
                <span className="text-xs text-slate-400 whitespace-nowrap">Cliquer pour choisir</span>
              </div>
            </div>
            
            {/* Boutons suivant */}
            <button
              onClick={() => navigateDate(1)}
              disabled={selectedDate >= new Date().toISOString().split('T')[0]}
              className="px-5 py-2 rounded-xl bg-purple-900/40 hover:bg-purple-800/50 text-purple-300 hover:text-white transition-all font-bold border border-purple-500/30 hover:border-purple-400/50 disabled:opacity-30 disabled:cursor-not-allowed"
            >
              Jour suivant ›
            </button>
            <button
              onClick={() => navigateDate(7)}
              disabled={selectedDate >= new Date().toISOString().split('T')[0]}
              className="px-4 py-2 rounded-xl bg-slate-700/50 hover:bg-slate-600/50 text-slate-300 hover:text-white transition-all font-medium border border-slate-600/30 hover:border-slate-500/50 disabled:opacity-30 disabled:cursor-not-allowed"
            >
              +7j »
            </button>
          </div>
          
          {/* Affichage date sélectionnée */}
          <p className="text-center mt-4 text-lg font-bold text-white capitalize">
            📅 {formatDateDisplay(selectedDate)}
          </p>
        </div>

        {/* Stats du jour - Cards premium */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="p-5 rounded-2xl bg-gradient-to-br from-slate-800/90 to-slate-900/90 border border-slate-700/50 backdrop-blur text-center shadow-xl hover:scale-105 transition-transform">
            <p className="text-4xl font-black text-white mb-1">{stats.total}</p>
            <p className="text-sm text-slate-400 font-medium">Matchs analysés</p>
          </div>
          <div className="p-5 rounded-2xl bg-gradient-to-br from-green-900/40 to-green-950/40 border border-green-500/30 backdrop-blur text-center shadow-xl shadow-green-900/20 hover:scale-105 transition-transform">
            <p className="text-4xl font-black text-green-400 mb-1">{stats.correct}</p>
            <p className="text-sm text-green-400/70 font-medium">Prédictions ✅</p>
          </div>
          <div className="p-5 rounded-2xl bg-gradient-to-br from-red-900/40 to-red-950/40 border border-red-500/30 backdrop-blur text-center shadow-xl shadow-red-900/20 hover:scale-105 transition-transform">
            <p className="text-4xl font-black text-red-400 mb-1">{stats.wrong}</p>
            <p className="text-sm text-red-400/70 font-medium">Incorrectes ❌</p>
          </div>
          <div className={`p-5 rounded-2xl backdrop-blur text-center shadow-xl hover:scale-105 transition-transform ${
            successRate >= 70 
              ? 'bg-gradient-to-br from-emerald-900/50 to-emerald-950/50 border border-emerald-400/40 shadow-emerald-900/30'
              : successRate >= 50 
                ? 'bg-gradient-to-br from-yellow-900/40 to-amber-950/40 border border-yellow-500/30 shadow-yellow-900/20'
                : 'bg-gradient-to-br from-orange-900/40 to-red-950/40 border border-orange-500/30 shadow-orange-900/20'
          }`}>
            <p className={`text-4xl font-black mb-1 ${
              successRate >= 70 ? 'text-emerald-400' : successRate >= 50 ? 'text-yellow-400' : 'text-orange-400'
            }`}>{successRate}%</p>
            <p className={`text-sm font-medium ${
              successRate >= 70 ? 'text-emerald-400/70' : successRate >= 50 ? 'text-yellow-400/70' : 'text-orange-400/70'
            }`}>Taux de réussite</p>
          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-16">
            <div className="w-16 h-16 border-4 border-purple-500/30 border-t-purple-500 rounded-full animate-spin mb-4" />
            <p className="text-slate-400">Chargement de l'historique...</p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="text-center py-12 bg-red-900/20 rounded-2xl border border-red-500/30">
            <span className="text-5xl mb-4 block">⚠️</span>
            <p className="text-red-400 text-lg mb-4">{error}</p>
            <button 
              onClick={() => window.location.reload()}
              className="px-6 py-2 rounded-xl bg-gradient-to-r from-red-600 to-red-500 text-white font-bold hover:from-red-500 hover:to-red-400 transition-all"
            >
              Réessayer
            </button>
          </div>
        )}

        {/* Matchs du jour */}
        {!loading && !error && matches.length > 0 && (
          <div className="space-y-3">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              🏟️ Résultats du jour
              <span className="px-3 py-1 rounded-full bg-indigo-900/50 text-indigo-300 text-sm font-medium">
                {matches.length} matchs
              </span>
            </h2>
            
            {matches.map(match => (
              <MatchResultCard key={match.id} match={match} />
            ))}
          </div>
        )}

        {/* Vide */}
        {!loading && !error && matches.length === 0 && (
          <div className="text-center py-20 bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-3xl border border-slate-700/30">
            <span className="text-7xl mb-6 block">📭</span>
            <p className="text-slate-300 text-xl font-medium mb-2">Aucun match terminé</p>
            <p className="text-slate-500">pour le {formatDateDisplay(selectedDate)}</p>
            <button
              onClick={() => navigateDate(-1)}
              className="mt-6 px-6 py-3 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold hover:from-purple-500 hover:to-indigo-500 transition-all shadow-lg shadow-purple-900/30"
            >
              ← Voir la veille
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Carte de résultat de match avec design premium
 */
function MatchResultCard({ match }: { match: Match & { _success?: MatchSuccess | null } }) {
  const prediction = match.prediction;
  const actualHome = match.score_home ?? 0;
  const actualAway = match.score_away ?? 0;
  const predHome = prediction?.home_score_forecast ?? 0;
  const predAway = prediction?.away_score_forecast ?? 0;
  
  // Déterminer le résultat
  const actualWinner = actualHome > actualAway ? 'home' : actualAway > actualHome ? 'away' : 'draw';
  const predWinner = predHome > predAway ? 'home' : predAway > predHome ? 'away' : 'draw';
  const isWinnerCorrect = actualWinner === predWinner;
  const isScoreCorrect = actualHome === predHome && actualAway === predAway;
  
  return (
    <Link
      to={`/matches/${match.id}`}
      className={`block p-4 rounded-2xl border transition-all hover:scale-[1.01] hover:shadow-xl ${
        isWinnerCorrect 
          ? 'bg-gradient-to-r from-green-900/20 to-slate-900/40 border-green-500/30 hover:border-green-400/50' 
          : 'bg-gradient-to-r from-red-900/20 to-slate-900/40 border-red-500/30 hover:border-red-400/50'
      }`}
    >
      <div className="flex items-center gap-4">
        {/* Indicateur succès/échec */}
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-xl font-bold ${
          isScoreCorrect 
            ? 'bg-gradient-to-br from-emerald-500 to-green-600 text-white shadow-lg shadow-emerald-500/30' 
            : isWinnerCorrect 
              ? 'bg-gradient-to-br from-green-600 to-green-700 text-white shadow-lg shadow-green-500/20' 
              : 'bg-gradient-to-br from-red-600 to-red-700 text-white shadow-lg shadow-red-500/20'
        }`}>
          {isScoreCorrect ? '🎯' : isWinnerCorrect ? '✓' : '✗'}
        </div>
        
        {/* Drapeau compétition */}
        <span className="text-2xl">{COMP_FLAGS[match.competition_code] || '⚽'}</span>
        
        {/* Équipes et scores */}
        <div className="flex-1 flex items-center justify-between gap-4">
          {/* Équipe domicile */}
          <div className={`flex items-center gap-2 flex-1 ${actualWinner === 'home' ? 'font-bold' : ''}`}>
            {match.home_team_crest && (
              <img src={match.home_team_crest} alt="" className="w-6 h-6 object-contain" />
            )}
            <span className={`text-sm truncate ${actualWinner === 'home' ? 'text-white' : 'text-slate-300'}`}>
              {match.home_team_short || match.home_team}
            </span>
          </div>
          
          {/* Score réel */}
          <div className="px-4 py-2 rounded-xl bg-slate-800/80 border border-slate-600/50 text-center min-w-[80px]">
            <span className="text-xl font-black text-white">
              {actualHome} - {actualAway}
            </span>
          </div>
          
          {/* Équipe extérieur */}
          <div className={`flex items-center gap-2 flex-1 justify-end ${actualWinner === 'away' ? 'font-bold' : ''}`}>
            <span className={`text-sm truncate ${actualWinner === 'away' ? 'text-white' : 'text-slate-300'}`}>
              {match.away_team_short || match.away_team}
            </span>
            {match.away_team_crest && (
              <img src={match.away_team_crest} alt="" className="w-6 h-6 object-contain" />
            )}
          </div>
        </div>
        
        {/* Prédiction */}
        {prediction && (
          <div className={`px-3 py-1.5 rounded-lg text-sm font-bold whitespace-nowrap ${
            isScoreCorrect 
              ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
              : isWinnerCorrect 
                ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                : 'bg-red-500/20 text-red-400 border border-red-500/30'
          }`}>
            Prédit: {predHome}-{predAway}
          </div>
        )}
      </div>
    </Link>
  );
}
