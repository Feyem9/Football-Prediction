/**
 * History Page - Historique des Matchs (Version Simplifiée)
 * Affiche les matchs terminés avec prédiction vs résultat
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import type { Match } from '../types';

const API_BASE = 'https://football-prediction-mbil.onrender.com/api/v1';

const COMP_EMOJIS: Record<string, string> = {
  PL: '🏴󠁧󠁢󠁥󠁮󠁧󠁿', FL1: '🇫🇷', BL1: '🇩🇪', SA: '🇮🇹', PD: '🇪🇸', CL: '🏆',
};

export default function History() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState({ total: 0, correct: 0, wrong: 0 });

  useEffect(() => {
    const fetchFinishedMatches = async () => {
      try {
        setLoading(true);
        // Appel direct à l'API pour les matchs terminés
        const response = await fetch(`${API_BASE}/matches?status=FINISHED&limit=50`);
        if (!response.ok) throw new Error('Erreur API');
        
        const data = await response.json();
        console.log('📊 Matchs reçus:', data.count);
        
        const finishedMatches = data.matches.filter((m: Match) => 
          m.score_home !== null && m.score_home !== undefined
        );
        
        setMatches(finishedMatches);
        
        // Calculer les stats
        let correct = 0, wrong = 0;
        finishedMatches.forEach((m: Match) => {
          if (m.prediction) {
            if (isPredictionCorrect(m)) correct++;
            else wrong++;
          }
        });
        setStats({ total: finishedMatches.length, correct, wrong });
        
      } catch (err) {
        console.error('Erreur:', err);
        setError('Impossible de charger les matchs');
      } finally {
        setLoading(false);
      }
    };
    
    fetchFinishedMatches();
  }, []);

  // Grouper les matchs par date
  const matchesByDate = matches.reduce((acc, match) => {
    const date = new Date(match.match_date).toLocaleDateString('fr-FR', {
      weekday: 'long', day: 'numeric', month: 'long'
    });
    if (!acc[date]) acc[date] = [];
    acc[date].push(match);
    return acc;
  }, {} as Record<string, Match[]>);

  const successRate = stats.total > 0 ? Math.round((stats.correct / stats.total) * 100) : 0;

  return (
    <div className="min-h-screen pb-16">
      {/* Hero */}
      <div className="relative py-10 mb-6">
        <div className="absolute inset-0 bg-gradient-to-r from-indigo-600/20 via-purple-600/10 to-transparent" />
        <div className="relative container mx-auto px-4 text-center">
          <span className="text-4xl mb-3 block">📊</span>
          <h1 className="text-3xl md:text-4xl font-black text-white mb-2">
            Historique <span className="text-indigo-400">des Résultats</span>
          </h1>
          <p className="text-slate-400">Matchs terminés avec analyse des prédictions</p>
        </div>
      </div>

      <div className="container mx-auto px-4 max-w-4xl">
        {/* Stats Globales */}
        <div className="grid grid-cols-4 gap-3 mb-8">
          <div className="p-4 rounded-xl bg-slate-800/70 border border-slate-700 text-center">
            <p className="text-3xl font-black text-white">{stats.total}</p>
            <p className="text-xs text-slate-500">Matchs</p>
          </div>
          <div className="p-4 rounded-xl bg-green-900/30 border border-green-500/50 text-center">
            <p className="text-3xl font-black text-green-400">{stats.correct}</p>
            <p className="text-xs text-green-400/70">Corrects ✅</p>
          </div>
          <div className="p-4 rounded-xl bg-red-900/30 border border-red-500/50 text-center">
            <p className="text-3xl font-black text-red-400">{stats.wrong}</p>
            <p className="text-xs text-red-400/70">Incorrects ❌</p>
          </div>
          <div className="p-4 rounded-xl bg-indigo-900/30 border border-indigo-500/50 text-center">
            <p className="text-3xl font-black text-indigo-400">{successRate}%</p>
            <p className="text-xs text-indigo-400/70">Taux succès</p>
          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div className="flex justify-center py-12">
            <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="text-center py-12 bg-red-900/20 rounded-2xl border border-red-500/30">
            <span className="text-4xl mb-4 block">⚠️</span>
            <p className="text-red-400">{error}</p>
            <button 
              onClick={() => window.location.reload()}
              className="mt-4 px-6 py-2 rounded-xl bg-indigo-500 text-white font-bold"
            >
              Réessayer
            </button>
          </div>
        )}

        {/* Liste des Matchs par Date */}
        {!loading && !error && Object.keys(matchesByDate).length > 0 && (
          <div className="space-y-8">
            {Object.entries(matchesByDate).map(([date, dateMatches]) => {
              // Calculer les stats du jour
              let dayCorrect = 0, dayWrong = 0;
              dateMatches.forEach(m => {
                if (m.prediction) {
                  if (isPredictionCorrect(m)) dayCorrect++;
                  else dayWrong++;
                }
              });
              const dayTotal = dateMatches.length;
              const dayRate = (dayCorrect + dayWrong) > 0 
                ? Math.round((dayCorrect / (dayCorrect + dayWrong)) * 100) 
                : 0;
              
              return (
                <div key={date} className="bg-slate-800/30 rounded-2xl p-5 border border-slate-700/50">
                  {/* Header du Jour avec Stats */}
                  <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
                    <h2 className="text-lg font-bold text-white capitalize flex items-center gap-2">
                      📅 {date}
                    </h2>
                    
                    {/* Stats du Jour */}
                    <div className="flex items-center gap-3">
                      <span className="px-3 py-1 rounded-lg bg-slate-700/50 text-slate-300 text-sm font-bold">
                        {dayTotal} match{dayTotal > 1 ? 's' : ''}
                      </span>
                      <span className="px-3 py-1 rounded-lg bg-green-900/30 text-green-400 text-sm font-bold">
                        ✅ {dayCorrect}
                      </span>
                      <span className="px-3 py-1 rounded-lg bg-red-900/30 text-red-400 text-sm font-bold">
                        ❌ {dayWrong}
                      </span>
                      <span className={`px-3 py-1.5 rounded-lg text-sm font-black ${
                        dayRate >= 70 ? 'bg-green-500 text-white' :
                        dayRate >= 50 ? 'bg-yellow-500 text-black' :
                        'bg-red-500 text-white'
                      }`}>
                        {dayRate}%
                      </span>
                    </div>
                  </div>
                  
                  {/* Matchs du Jour */}
                  <div className="space-y-3">
                    {dateMatches.map(match => (
                      <MatchResultCard key={match.id} match={match} />
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Vide */}
        {!loading && !error && matches.length === 0 && (
          <div className="text-center py-16 bg-slate-800/30 rounded-3xl">
            <span className="text-6xl mb-4 block">📭</span>
            <p className="text-slate-400 text-lg">Aucun match terminé disponible</p>
            <p className="text-slate-500 text-sm mt-2">
              Les résultats apparaîtront ici une fois les matchs terminés
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * MatchResultCard - Carte de résultat avec prédiction
 */
function MatchResultCard({ match }: { match: Match }) {
  const pred = match.prediction;
  const isCorrect = pred ? isPredictionCorrect(match) : null;
  const [expanded, setExpanded] = useState(false);

  return (
    <div className={`rounded-2xl overflow-hidden transition-all ${
      isCorrect === true ? 'bg-green-900/20 border border-green-500/30' :
      isCorrect === false ? 'bg-red-900/20 border border-red-500/30' :
      'bg-slate-800/70 border border-slate-700'
    }`}>
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-4 flex items-center gap-3 text-left hover:bg-white/5 transition-colors"
      >
        {/* Status Icon */}
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-lg ${
          isCorrect === true ? 'bg-green-500/30' :
          isCorrect === false ? 'bg-red-500/30' :
          'bg-slate-700'
        }`}>
          {isCorrect === true ? '✅' : isCorrect === false ? '❌' : '❓'}
        </div>

        {/* Competition */}
        <span className="text-lg">{COMP_EMOJIS[match.competition_code || ''] || '⚽'}</span>

        {/* Teams & Score */}
        <div className="flex-1 flex items-center justify-center gap-3">
          <span className="font-bold text-white text-right flex-1 truncate">{match.home_team_short}</span>
          <span className="px-3 py-1.5 rounded-lg bg-indigo-500/30 text-indigo-300 font-black text-lg min-w-[60px] text-center">
            {match.score_home} - {match.score_away}
          </span>
          <span className="font-bold text-white text-left flex-1 truncate">{match.away_team_short}</span>
        </div>

        {/* Prediction mini */}
        {pred && (
          <span className={`px-2 py-1 rounded text-xs font-bold ${
            isCorrect ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
          }`}>
            Prédit: {pred.home_score_forecast}-{pred.away_score_forecast}
          </span>
        )}

        {/* Arrow */}
        <span className={`text-slate-400 transition-transform ${expanded ? 'rotate-180' : ''}`}>▼</span>
      </button>

      {/* Expanded Content */}
      {expanded && pred && (
        <div className="p-4 bg-slate-900/30 border-t border-slate-700/50 space-y-4">
          {/* Breakdown des 3 Logiques */}
          <div className="grid grid-cols-3 gap-3">
            {/* 1. Logique de Papa */}
            {(() => {
              const papaHome = pred.papa_home_score ?? pred.home_score_forecast;
              const papaAway = pred.papa_away_score ?? pred.away_score_forecast;
              const papaConf = pred.papa_confidence ?? pred.confidence;
              
              const actualResult = match.score_home! > match.score_away! ? '1' : 
                                   match.score_home! < match.score_away! ? '2' : 'X';
              const papaResult = papaHome > papaAway ? '1' : papaHome < papaAway ? '2' : 'X';
              const isPapaCorrect = actualResult === papaResult;
              
              return (
                <div className={`p-3 rounded-xl text-center ${
                  isPapaCorrect ? 'bg-green-900/30 border border-green-500/30' : 'bg-red-900/30 border border-red-500/30'
                }`}>
                  <p className="text-xs text-slate-500 mb-1">🟢 Papa</p>
                  <p className="text-lg font-bold">
                    {isPapaCorrect ? '✅' : '❌'}
                  </p>
                  <p className="text-sm text-white font-bold">{papaHome}-{papaAway}</p>
                  <p className="text-xs text-slate-400">{Math.round(papaConf * 100)}%</p>
                </div>
              );
            })()}

            {/* 2. Logique Grand Frère */}
            {(() => {
              const gfHome = pred.grand_frere_home_score ?? pred.home_score_forecast;
              const gfAway = pred.grand_frere_away_score ?? pred.away_score_forecast;
              const gfConf = pred.grand_frere_confidence ?? pred.confidence;
              
              const actualResult = match.score_home! > match.score_away! ? '1' : 
                                   match.score_home! < match.score_away! ? '2' : 'X';
              const gfResult = gfHome > gfAway ? '1' : gfHome < gfAway ? '2' : 'X';
              const isGfCorrect = actualResult === gfResult;
              
              return (
                <div className={`p-3 rounded-xl text-center ${
                  isGfCorrect ? 'bg-green-900/30 border border-green-500/30' : 'bg-red-900/30 border border-red-500/30'
                }`}>
                  <p className="text-xs text-slate-500 mb-1">🔵 Grand Frère</p>
                  <p className="text-lg font-bold">
                    {isGfCorrect ? '✅' : '❌'}
                  </p>
                  <p className="text-sm text-white font-bold">{gfHome}-{gfAway}</p>
                  <p className="text-xs text-slate-400">{Math.round(gfConf * 100)}%</p>
                </div>
              );
            })()}

            {/* 3. Ma Logique */}
            {(() => {
              const mlHome = pred.ma_logique_home_score ?? pred.home_score_forecast;
              const mlAway = pred.ma_logique_away_score ?? pred.away_score_forecast;
              const mlConf = pred.ma_logique_confidence ?? pred.confidence;
              
              const actualResult = match.score_home! > match.score_away! ? '1' : 
                                   match.score_home! < match.score_away! ? '2' : 'X';
              const mlResult = mlHome > mlAway ? '1' : mlHome < mlAway ? '2' : 'X';
              const isMlCorrect = actualResult === mlResult;
              
              return (
                <div className={`p-3 rounded-xl text-center ${
                  isMlCorrect ? 'bg-green-900/30 border border-green-500/30' : 'bg-red-900/30 border border-red-500/30'
                }`}>
                  <p className="text-xs text-slate-500 mb-1">🟡 Ma Logique</p>
                  <p className="text-lg font-bold">
                    {isMlCorrect ? '✅' : '❌'}
                  </p>
                  <p className="text-sm text-white font-bold">{mlHome}-{mlAway}</p>
                  <p className="text-xs text-slate-400">{Math.round(mlConf * 100)}%</p>
                </div>
              );
            })()}
          </div>

          {/* Tip et Confiance */}
          <div className="flex items-center justify-between p-3 rounded-xl bg-slate-800/50">
            <div>
              <p className="text-xs text-slate-500">Conseil du jour</p>
              <p className="text-white font-bold">{pred.bet_tip}</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-slate-500">Confiance</p>
              <p className="text-indigo-400 font-black text-lg">{Math.round((pred.confidence || 0) * 100)}%</p>
            </div>
          </div>

          {/* Link to detail */}
          <Link 
            to={`/matches/${match.id}`}
            className="block text-center py-2 rounded-xl bg-indigo-500/20 text-indigo-400 font-bold hover:bg-indigo-500/30 transition-colors"
          >
            Voir l'analyse complète →
          </Link>
        </div>
      )}
    </div>
  );
}

/**
 * Vérifie si la prédiction était correcte (résultat 1X2)
 */
function isPredictionCorrect(match: Match): boolean {
  const pred = match.prediction;
  if (!pred || match.score_home === null || match.score_away === null) return false;
  
  const actualHome = match.score_home;
  const actualAway = match.score_away;
  
  // Résultat réel: 1=home, X=draw, 2=away
  const actualResult = actualHome > actualAway ? '1' : actualHome < actualAway ? '2' : 'X';
  
  // Résultat prédit
  const predResult = pred.home_score_forecast > pred.away_score_forecast ? '1' : 
                     pred.home_score_forecast < pred.away_score_forecast ? '2' : 'X';
  
  // Vérifier si le résultat correspond
  if (actualResult === predResult) return true;
  
  // Vérifier aussi les tips buts
  const tip = pred.bet_tip || '';
  const totalGoals = actualHome + actualAway;
  
  if (tip.includes('Plus de 2.5') && totalGoals > 2.5) return true;
  if (tip.includes('Moins de 2.5') && totalGoals < 2.5) return true;
  
  return false;
}
