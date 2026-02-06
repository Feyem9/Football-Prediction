/**
 * MatchCard Component - Design Premium avec Animations
 */
import { Link } from 'react-router-dom';
import type { Match } from '../../types';

interface MatchCardProps {
  match: Match;
}

export default function MatchCard({ match }: MatchCardProps) {
  const isFinished = match.status === 'FINISHED';
  const isLive = match.status === 'IN_PLAY' || match.status === 'PAUSED';
  const isScheduled = match.status === 'SCHEDULED' || match.status === 'TIMED';
  
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    const isToday = date.toDateString() === now.toDateString();
    const isTomorrow = date.toDateString() === tomorrow.toDateString();
    
    if (isToday) return `Aujourd'hui ${date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}`;
    if (isTomorrow) return `Demain ${date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}`;
    
    return date.toLocaleDateString('fr-FR', { 
      weekday: 'short', 
      day: 'numeric', 
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Couleurs par compétition
  const compColors: Record<string, string> = {
    PL: 'from-purple-600 to-purple-800',
    FL1: 'from-blue-600 to-blue-800',
    BL1: 'from-red-600 to-red-800',
    SA: 'from-green-600 to-green-800',
    PD: 'from-orange-600 to-orange-800',
    CL: 'from-blue-500 to-indigo-700',
  };

  const gradient = compColors[match.competition_code] || 'from-slate-600 to-slate-800';

  return (
    <Link 
      to={`/matches/${match.id}`}
      className="group relative block overflow-hidden rounded-2xl transition-all duration-500 hover:scale-[1.02] hover:shadow-2xl hover:shadow-blue-500/20"
    >
      {/* Background Gradient */}
      <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-20 group-hover:opacity-30 transition-opacity`} />
      
      {/* Glass Card */}
      <div className="relative bg-slate-900/70 backdrop-blur-xl border border-slate-700/50 group-hover:border-blue-500/50 p-5 transition-all duration-300">
        
        {/* Header */}
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center gap-2">
            <span className={`text-xs font-bold px-3 py-1.5 rounded-full bg-gradient-to-r ${gradient} text-white shadow-lg`}>
              {match.competition_code}
            </span>
            {match.matchday && (
              <span className="text-xs text-slate-500">J{match.matchday}</span>
            )}
          </div>
          
          {isLive ? (
            <span className="flex items-center gap-2 text-xs font-bold text-red-400 bg-red-500/20 px-3 py-1.5 rounded-full border border-red-500/50 animate-pulse">
              <span className="w-2 h-2 bg-red-500 rounded-full animate-ping" />
              LIVE
            </span>
          ) : isFinished ? (
            <span className="text-xs text-emerald-400 bg-emerald-500/20 px-3 py-1.5 rounded-full">
              Terminé
            </span>
          ) : (
            <span className="text-xs text-slate-400">
              {formatDate(match.match_date)}
            </span>
          )}
        </div>

        {/* Teams */}
        <div className="flex items-center justify-between gap-4 mb-4">
          {/* Home */}
          <div className="flex-1 text-center">
            <p className="font-bold text-white text-sm md:text-base truncate group-hover:text-blue-300 transition-colors">
              {match.home_team}
            </p>
          </div>

          {/* Score */}
          <div className="flex-shrink-0">
            {isFinished || isLive ? (
              <div className="flex items-center gap-3 px-4 py-2 rounded-xl bg-slate-800/80 border border-slate-600">
                <span className="text-2xl font-black text-white">{match.score_home ?? 0}</span>
                <span className="text-slate-500">:</span>
                <span className="text-2xl font-black text-white">{match.score_away ?? 0}</span>
              </div>
            ) : match.prediction ? (
              <div className="flex items-center gap-3 px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600/30 to-purple-600/30 border border-blue-500/50">
                <span className="text-2xl font-black text-blue-400">{match.prediction.home_score_forecast}</span>
                <span className="text-blue-300/50">:</span>
                <span className="text-2xl font-black text-blue-400">{match.prediction.away_score_forecast}</span>
              </div>
            ) : (
              <div className="px-6 py-2 rounded-xl bg-slate-800/50 border border-slate-700">
                <span className="text-lg font-bold text-slate-500">VS</span>
              </div>
            )}
          </div>

          {/* Away */}
          <div className="flex-1 text-center">
            <p className="font-bold text-white text-sm md:text-base truncate group-hover:text-blue-300 transition-colors">
              {match.away_team}
            </p>
          </div>
        </div>

        {/* Prediction Tip */}
        {match.prediction && isScheduled && (
          <div className="flex items-center justify-center gap-4 pt-3 border-t border-slate-700/50">
            <div className="flex items-center gap-2">
              <span className="text-yellow-500">🎯</span>
              <span className="text-sm font-semibold text-yellow-400">
                {match.prediction.bet_tip}
              </span>
            </div>
            <div className="flex items-center gap-1">
              <div className="h-2 w-16 bg-slate-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-green-500 to-emerald-400 rounded-full transition-all duration-500"
                  style={{ width: `${Math.round(match.prediction.confidence * 100)}%` }}
                />
              </div>
              <span className="text-xs text-slate-400">
                {Math.round(match.prediction.confidence * 100)}%
              </span>
            </div>
          </div>
        )}

        {/* Cotes de Paris */}
        {isScheduled && (match.odds_home || match.odds_draw || match.odds_away) && (
          <div className="flex items-center justify-center gap-2 pt-3 mt-2 border-t border-slate-700/50">
            <span className="text-xs text-slate-500 mr-2">Cotes:</span>
            {match.odds_home && (
              <span className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                match.prediction?.ma_logique_home_score && match.prediction?.ma_logique_away_score &&
                match.prediction.ma_logique_home_score > match.prediction.ma_logique_away_score
                  ? 'bg-green-500/20 text-green-400 border border-green-500/50'
                  : 'bg-slate-700/50 text-slate-300'
              }`}>
                1: {match.odds_home.toFixed(2)}
              </span>
            )}
            {match.odds_draw && (
              <span className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                match.prediction?.ma_logique_home_score === match.prediction?.ma_logique_away_score
                  ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/50'
                  : 'bg-slate-700/50 text-slate-300'
              }`}>
                X: {match.odds_draw.toFixed(2)}
              </span>
            )}
            {match.odds_away && (
              <span className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                match.prediction?.ma_logique_away_score && match.prediction?.ma_logique_home_score &&
                match.prediction.ma_logique_away_score > match.prediction.ma_logique_home_score
                  ? 'bg-blue-500/20 text-blue-400 border border-blue-500/50'
                  : 'bg-slate-700/50 text-slate-300'
              }`}>
                2: {match.odds_away.toFixed(2)}
              </span>
            )}
          </div>
        )}

        {/* Hover Effect Line */}
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-500 origin-left" />
      </div>
    </Link>
  );
}
