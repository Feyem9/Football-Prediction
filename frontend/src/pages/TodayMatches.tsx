/**
 * TodayMatches Page - Matchs du Jour avec Scores Live
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getTodayMatches } from '../lib/api';
import type { Match } from '../types';

export default function TodayMatches() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const fetchData = async () => {
    try {
      const data = await getTodayMatches();
      setMatches(data.matches);
      setLastUpdate(new Date());
      setError(null);
    } catch (err) {
      setError('Erreur lors du chargement des matchs');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    
    // Auto-refresh toutes les 60 secondes pour les scores live
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, []);

  // Organiser par statut
  const finishedMatches = matches.filter(m => m.status === 'FINISHED');
  const liveMatches = matches.filter(m => m.status === 'IN_PLAY' || m.status === 'PAUSED');
  const upcomingMatches = matches.filter(m => m.status === 'SCHEDULED' || m.status === 'TIMED');

  const today = new Date().toLocaleDateString('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });

  return (
    <div className="min-h-screen pb-16">
      {/* Hero */}
      <div className="relative py-12 mb-8">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 via-purple-600/10 to-transparent" />
        <div className="relative container mx-auto px-4 text-center">
          <span className="text-5xl mb-4 block">📅</span>
          <h1 className="text-3xl md:text-5xl font-black text-white mb-2">
            Matchs du Jour
          </h1>
          <p className="text-slate-400 capitalize">{today}</p>
          <p className="text-xs text-slate-500 mt-2">
            Dernière mise à jour: {lastUpdate.toLocaleTimeString('fr-FR')}
          </p>
        </div>
      </div>

      <div className="container mx-auto px-4">
        {/* Loading */}
        {loading && (
          <div className="flex justify-center py-20">
            <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {/* Error */}
        {error && !loading && (
          <div className="text-center py-12 rounded-2xl bg-slate-800/50">
            <span className="text-5xl mb-4 block">⚠️</span>
            <p className="text-red-400">{error}</p>
          </div>
        )}

        {!loading && !error && (
          <>
            {/* MATCHS EN COURS - LIVE */}
            {liveMatches.length > 0 && (
              <section className="mb-12">
                <div className="flex items-center gap-3 mb-6">
                  <span className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
                  <h2 className="text-2xl font-bold text-red-400">🔴 En Cours ({liveMatches.length})</h2>
                  <button 
                    onClick={fetchData}
                    className="ml-auto px-4 py-2 rounded-lg bg-slate-700 text-sm text-slate-300 hover:bg-slate-600 transition-colors"
                  >
                    🔄 Actualiser
                  </button>
                </div>
                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {liveMatches.map(match => (
                    <LiveMatchCard key={match.id} match={match} />
                  ))}
                </div>
              </section>
            )}

            {/* MATCHS À VENIR */}
            {upcomingMatches.length > 0 && (
              <section className="mb-12">
                <div className="flex items-center gap-3 mb-6">
                  <span className="text-2xl">⏰</span>
                  <h2 className="text-2xl font-bold text-yellow-400">À Venir ({upcomingMatches.length})</h2>
                </div>
                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {upcomingMatches.map(match => (
                    <UpcomingMatchCard key={match.id} match={match} />
                  ))}
                </div>
              </section>
            )}

            {/* MATCHS TERMINÉS */}
            {finishedMatches.length > 0 && (
              <section className="mb-12">
                <div className="flex items-center gap-3 mb-6">
                  <span className="text-2xl">✅</span>
                  <h2 className="text-2xl font-bold text-green-400">Terminés ({finishedMatches.length})</h2>
                </div>
                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {finishedMatches.map(match => (
                    <FinishedMatchCard key={match.id} match={match} />
                  ))}
                </div>
              </section>
            )}

            {/* Empty State */}
            {matches.length === 0 && (
              <div className="text-center py-20 rounded-2xl bg-slate-800/50">
                <span className="text-6xl mb-6 block">📭</span>
                <h3 className="text-xl font-bold text-white mb-2">Aucun match aujourd'hui</h3>
                <p className="text-slate-400 mb-6">Consultez les matchs à venir</p>
                <Link 
                  to="/" 
                  className="inline-block px-6 py-3 rounded-xl bg-blue-500 text-white font-semibold hover:bg-blue-600 transition-colors"
                >
                  Voir tous les matchs
                </Link>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

/**
 * LiveMatchCard - Match en cours avec score LIVE
 */
function LiveMatchCard({ match }: { match: Match }) {
  const homeScore = match.score_home ?? 0;
  const awayScore = match.score_away ?? 0;

  return (
    <Link 
      to={`/matches/${match.id}`}
      className="group relative block overflow-hidden rounded-2xl transition-all duration-300 hover:scale-[1.02]"
    >
      <div className="relative bg-gradient-to-br from-red-900/30 to-slate-900/70 backdrop-blur-xl border border-red-500/50 p-5">
        {/* Header avec LIVE badge */}
        <div className="flex justify-between items-center mb-4">
          <span className="text-xs font-bold px-3 py-1.5 rounded-full bg-slate-700 text-slate-300">
            {match.competition_code} • J{match.matchday}
          </span>
          <span className="flex items-center gap-2 text-xs text-red-400 bg-red-500/20 px-3 py-1.5 rounded-full animate-pulse">
            <span className="w-2 h-2 bg-red-500 rounded-full" />
            LIVE
          </span>
        </div>

        {/* Teams & LIVE Score */}
        <div className="flex items-center justify-between gap-4">
          <div className="flex-1 text-left">
            <p className={`font-bold text-sm ${homeScore > awayScore ? 'text-green-400' : 'text-white'}`}>
              {match.home_team_short || match.home_team}
            </p>
          </div>

          {/* Score en GRAND */}
          <div className="flex-shrink-0">
            <div className="flex items-center gap-4 px-6 py-3 rounded-xl bg-slate-800 border-2 border-red-500/50 shadow-lg shadow-red-500/20">
              <span className="text-4xl font-black text-white">{homeScore}</span>
              <span className="text-2xl text-red-400 animate-pulse">:</span>
              <span className="text-4xl font-black text-white">{awayScore}</span>
            </div>
          </div>

          <div className="flex-1 text-right">
            <p className={`font-bold text-sm ${awayScore > homeScore ? 'text-green-400' : 'text-white'}`}>
              {match.away_team_short || match.away_team}
            </p>
          </div>
        </div>
      </div>
    </Link>
  );
}

/**
 * UpcomingMatchCard - Match à venir
 */
function UpcomingMatchCard({ match }: { match: Match }) {
  const time = new Date(match.match_date).toLocaleTimeString('fr-FR', {
    hour: '2-digit',
    minute: '2-digit'
  });

  return (
    <Link 
      to={`/matches/${match.id}`}
      className="group relative block overflow-hidden rounded-2xl transition-all duration-300 hover:scale-[1.02]"
    >
      <div className="relative bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 p-5 hover:border-yellow-500/50 transition-colors">
        {/* Header */}
        <div className="flex justify-between items-center mb-4">
          <span className="text-xs font-bold px-3 py-1.5 rounded-full bg-slate-700 text-slate-300">
            {match.competition_code} • J{match.matchday}
          </span>
          <span className="text-xs text-yellow-400 bg-yellow-500/20 px-3 py-1.5 rounded-full font-bold">
            {time}
          </span>
        </div>

        {/* Teams */}
        <div className="flex items-center justify-between gap-4">
          <p className="font-bold text-white text-sm">{match.home_team_short || match.home_team}</p>
          <span className="text-2xl text-slate-500 font-bold">VS</span>
          <p className="font-bold text-white text-sm text-right">{match.away_team_short || match.away_team}</p>
        </div>

        {/* Prediction si disponible */}
        {match.prediction && (
          <div className="mt-4 pt-3 border-t border-slate-700/50 text-center">
            <span className="text-sm text-blue-400">
              Prédiction: {match.prediction.home_score_forecast} - {match.prediction.away_score_forecast}
            </span>
          </div>
        )}
      </div>
    </Link>
  );
}

/**
 * FinishedMatchCard - Match terminé avec résultat final
 */
function FinishedMatchCard({ match }: { match: Match }) {
  const homeScore = match.score_home ?? 0;
  const awayScore = match.score_away ?? 0;
  const predicted = match.prediction;
  
  // Déterminer le résultat réel
  let actualResult = 'X';
  if (homeScore > awayScore) actualResult = '1';
  else if (awayScore > homeScore) actualResult = '2';

  // Vérifier si la prédiction était correcte
  let predictionCorrect = false;
  if (predicted) {
    const predictedResult = predicted.bet_tip?.split(' ')[0] || '';
    predictionCorrect = predictedResult === actualResult || 
                        (predictedResult.includes('1') && actualResult === '1') ||
                        (predictedResult.includes('2') && actualResult === '2') ||
                        (predictedResult.includes('X') && actualResult === 'X');
  }

  return (
    <Link 
      to={`/matches/${match.id}`}
      className="group relative block overflow-hidden rounded-2xl transition-all duration-300 hover:scale-[1.02]"
    >
      <div className="relative bg-slate-900/70 backdrop-blur-xl border border-green-500/30 p-5">
        {/* Header */}
        <div className="flex justify-between items-center mb-4">
          <span className="text-xs font-bold px-3 py-1.5 rounded-full bg-slate-700 text-slate-300">
            {match.competition_code} • J{match.matchday}
          </span>
          <span className="text-xs text-green-400 bg-green-500/20 px-3 py-1.5 rounded-full">
            ✅ Terminé
          </span>
        </div>

        {/* Teams & Real Score */}
        <div className="flex items-center justify-between gap-4 mb-4">
          <div className="flex-1 text-left">
            <p className={`font-bold text-sm ${homeScore > awayScore ? 'text-green-400' : 'text-white'}`}>
              {match.home_team_short || match.home_team}
            </p>
          </div>

          <div className="flex-shrink-0">
            <div className="flex items-center gap-3 px-5 py-2 rounded-xl bg-slate-800 border border-green-500/50">
              <span className="text-3xl font-black text-white">{homeScore}</span>
              <span className="text-xl text-slate-500">-</span>
              <span className="text-3xl font-black text-white">{awayScore}</span>
            </div>
          </div>

          <div className="flex-1 text-right">
            <p className={`font-bold text-sm ${awayScore > homeScore ? 'text-green-400' : 'text-white'}`}>
              {match.away_team_short || match.away_team}
            </p>
          </div>
        </div>

        {/* Prediction Comparison */}
        {predicted && (
          <div className="pt-3 border-t border-slate-700/50">
            <div className="flex justify-between items-center text-sm">
              <span className="text-slate-500">Prédiction:</span>
              <span className="text-slate-400">
                {predicted.home_score_forecast} - {predicted.away_score_forecast}
              </span>
            </div>
            <div className="flex justify-between items-center text-sm mt-1">
              <span className="text-slate-500">Résultat:</span>
              <span className={predictionCorrect ? 'text-green-400 font-bold' : 'text-red-400'}>
                {predictionCorrect ? '✅ Correct' : '❌ Incorrect'}
              </span>
            </div>
          </div>
        )}
      </div>
    </Link>
  );
}
