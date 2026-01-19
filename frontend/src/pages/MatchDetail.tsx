/**
 * MatchDetail Page - Détail Match avec Prédictions Complètes et Preuves Réelles
 */
import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import LogicCard from '../components/predictions/LogicCard';
import { getMatch, getCombinedPrediction } from '../lib/api';
import type { Match, CombinedPrediction } from '../types';

export default function MatchDetail() {
  const { id } = useParams<{ id: string }>();
  const [match, setMatch] = useState<Match | null>(null);
  const [prediction, setPrediction] = useState<CombinedPrediction | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      if (!id) return;
      try {
        setLoading(true);
        const matchData = await getMatch(parseInt(id));
        setMatch(matchData);
        try {
          const predictionData = await getCombinedPrediction(parseInt(id));
          setPrediction(predictionData);
        } catch {
          setPrediction(null);
        }
      } catch (err) {
        setError('Match non trouvé');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-slate-400">Chargement de l'analyse...</p>
        </div>
      </div>
    );
  }

  if (error || !match) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Link to="/" className="text-blue-400 hover:text-blue-300 mb-4 inline-flex items-center gap-2">
          ← Retour aux matchs
        </Link>
        <div className="text-center py-12">
          <span className="text-6xl mb-4 block">⚠️</span>
          <p className="text-red-400 text-lg">{error || 'Match non trouvé'}</p>
        </div>
      </div>
    );
  }

  const isFinished = match.status === 'FINISHED';
  const isLive = match.status === 'IN_PLAY' || match.status === 'PAUSED';

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('fr-FR', {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Extraire les preuves RÉELLES des prédictions API
  const papaEvidence = prediction?.papa_prediction?.evidence;
  const grandFrereEvidence = prediction?.grand_frere_prediction?.evidence;
  const maLogiqueEvidence = prediction?.ma_logique_prediction?.evidence;

  return (
    <div className="min-h-screen pb-16">
      {/* Header Background */}
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-b from-blue-600/20 via-purple-600/10 to-transparent h-96" />
        
        <div className="relative container mx-auto px-4 pt-6">
          {/* Back Button */}
          <Link 
            to="/" 
            className="inline-flex items-center gap-2 text-slate-400 hover:text-white transition-colors mb-8"
          >
            <span>←</span> Retour aux matchs
          </Link>

          {/* Competition Badge */}
          <div className="text-center mb-6">
            <span className="inline-block px-4 py-2 rounded-full bg-slate-800/80 text-sm text-slate-300 border border-slate-700">
              {match.competition_name} • Journée {match.matchday}
            </span>
          </div>

          {/* Match Header */}
          <div className="flex flex-col md:flex-row items-center justify-center gap-6 md:gap-12 mb-8">
            {/* Home Team */}
            <div className="text-center md:text-right flex-1">
              <h2 className="text-2xl md:text-4xl font-black text-white">{match.home_team}</h2>
            </div>

            {/* Score / VS */}
            <div className="flex-shrink-0">
              {isFinished || isLive ? (
                <div className="flex items-center gap-4 px-8 py-4 rounded-2xl bg-slate-800/80 border border-slate-600">
                  <span className="text-5xl font-black text-white">{match.score_home}</span>
                  <span className="text-3xl text-slate-500">-</span>
                  <span className="text-5xl font-black text-white">{match.score_away}</span>
                </div>
              ) : (
                <div className="px-8 py-4">
                  <span className="text-4xl font-bold text-slate-500">VS</span>
                </div>
              )}
              {isLive && (
                <div className="text-center mt-2">
                  <span className="text-red-400 font-bold animate-pulse">🔴 EN DIRECT</span>
                </div>
              )}
            </div>

            {/* Away Team */}
            <div className="text-center md:text-left flex-1">
              <h2 className="text-2xl md:text-4xl font-black text-white">{match.away_team}</h2>
            </div>
          </div>

          {/* Date */}
          <p className="text-center text-slate-400 mb-8">
            {formatDate(match.match_date)}
          </p>
        </div>
      </div>

      {/* Prediction Section */}
      <div className="container mx-auto px-4">
        {prediction ? (
          <>
            {/* Final Prediction Banner */}
            <div className="mb-10 p-6 md:p-8 rounded-3xl bg-gradient-to-r from-blue-900/50 via-purple-900/50 to-pink-900/50 border border-blue-500/30">
              <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                <div className="flex items-center gap-4">
                  <span className="text-4xl">🎯</span>
                  <div>
                    <h3 className="text-xl font-bold text-white">Prédiction Finale</h3>
                    <p className="text-slate-400 text-sm">Combinaison des 3 logiques</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-8">
                  <div className="text-center">
                    <div className="flex items-center gap-3 px-6 py-3 rounded-xl bg-slate-900/50 border border-slate-700">
                      <span className="text-4xl font-black text-white">{prediction.final_home_goals}</span>
                      <span className="text-2xl text-slate-500">-</span>
                      <span className="text-4xl font-black text-white">{prediction.final_away_goals}</span>
                    </div>
                  </div>
                  
                  <div className="text-center">
                    <span className={`inline-block px-5 py-2.5 rounded-xl font-bold text-lg ${
                      prediction.consensus_level === 'FORT' ? 'bg-green-500/20 text-green-400 border border-green-500/50' :
                      prediction.consensus_level === 'MOYEN' ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/50' :
                      'bg-red-500/20 text-red-400 border border-red-500/50'
                    }`}>
                      {prediction.final_bet_tip.split(' - ')[0]}
                    </span>
                    <p className="text-xs text-slate-500 mt-2">
                      Consensus {prediction.consensus_level} • {Math.round(prediction.final_confidence * 100)}%
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Three Logic Cards - avec preuves RÉELLES */}
            <div className="grid md:grid-cols-3 gap-6">
              <LogicCard 
                name="papa" 
                prediction={prediction.papa_prediction} 
                evidence={papaEvidence}
                homeTeam={match.home_team}
                awayTeam={match.away_team}
              />
              <LogicCard 
                name="grand_frere" 
                prediction={prediction.grand_frere_prediction}
                evidence={grandFrereEvidence}
                homeTeam={match.home_team}
                awayTeam={match.away_team}
              />
              <LogicCard 
                name="ma_logique" 
                prediction={prediction.ma_logique_prediction}
                evidence={maLogiqueEvidence}
                homeTeam={match.home_team}
                awayTeam={match.away_team}
              />
            </div>

            {/* Consensus Explanation */}
            <div className="mt-10 p-6 rounded-2xl bg-slate-800/50 border border-slate-700/50">
              <h4 className="text-lg font-bold text-white mb-3">📖 Explication du Consensus</h4>
              <p className="text-slate-400">
                {prediction.all_agree 
                  ? "✅ Les 3 logiques sont d'accord sur le résultat. Confiance élevée !"
                  : prediction.consensus_level === 'MOYEN'
                    ? "⚠️ Les logiques ne sont pas toutes d'accord. Le consensus est modéré."
                    : "❌ Désaccord majeur entre les logiques. Prudence conseillée."
                }
              </p>
            </div>
          </>
        ) : (
          <div className="text-center py-16 rounded-2xl bg-slate-800/50 border border-slate-700/50">
            <span className="text-6xl mb-6 block">🔮</span>
            <h3 className="text-xl font-bold text-white mb-2">Prédiction non disponible</h3>
            <p className="text-slate-400">
              Les données nécessaires ne sont pas encore disponibles pour ce match.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
