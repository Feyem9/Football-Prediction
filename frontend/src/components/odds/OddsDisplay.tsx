/**
 * OddsDisplay Component - Affiche les cotes de paris et l'analyse Value Bet
 */
import { useState, useEffect, useCallback } from 'react';
import { refreshMatchOdds, getValueBet } from '../../lib/api';
import type { Match, ValueBetResponse } from '../../types';

interface OddsDisplayProps {
  match: Match;
}

export default function OddsDisplay({ match }: OddsDisplayProps) {
  const [valueBets, setValueBets] = useState<Record<string, ValueBetResponse>>({});
  const [refreshing, setRefreshing] = useState(false);
  const [odds, setOdds] = useState({
    home: match.odds_home,
    draw: match.odds_draw,
    away: match.odds_away,
  });

  const hasOdds = !!(odds.home || odds.draw || odds.away);

  // Analyser les value bets
  const analyzeValueBets = useCallback(async (h?: number | null, d?: number | null, a?: number | null) => {
    const currentH = h ?? odds.home;
    const currentD = d ?? odds.draw;
    const currentA = a ?? odds.away;

    if (!currentH && !currentD && !currentA) return;
    
    console.log('🧠 Analyse des value bets...');
    const results: Record<string, ValueBetResponse> = {};
    const betTypes: ('home' | 'draw' | 'away')[] = ['home', 'draw', 'away'];
    
    for (const betType of betTypes) {
      try {
        const data = await getValueBet(match.id, betType);
        results[betType] = data;
      } catch (error) {
        console.error(`Erreur analyse ${betType}:`, error);
      }
    }
    
    setValueBets(results);
  }, [match.id, odds.home, odds.draw, odds.away]);

  // Rafraîchir les cotes
  const handleRefresh = async (e?: React.MouseEvent) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    
    console.log('🔄 Rafraîchissement des cotes...');
    setRefreshing(true);
    try {
      const data = await refreshMatchOdds(match.id);
      setOdds({
        home: data.odds_home,
        draw: data.odds_draw,
        away: data.odds_away,
      });
      // L'analyse sera déclenchée par l'effet de mise à jour des cotes
    } catch (error) {
      console.error('❌ Erreur:', error);
    } finally {
      setRefreshing(false);
    }
  };

  // Analyser au chargement
  useEffect(() => {
    if (hasOdds) {
      analyzeValueBets();
    }
  }, [hasOdds, analyzeValueBets]);

  const impliedProb = (odd: number) => ((1 / odd) * 100).toFixed(1);

  const getValueColor = (vb: ValueBetResponse | undefined) => {
    if (!vb) return 'text-slate-400';
    if (vb.value_percentage > 10) return 'text-green-400';
    if (vb.value_percentage > 5) return 'text-yellow-400';
    if (vb.value_percentage > 0) return 'text-orange-400';
    return 'text-red-400';
  };

  const getValueBg = (vb: ValueBetResponse | undefined) => {
    if (!vb) return 'bg-slate-800/50 border-slate-700';
    if (vb.is_value_bet && vb.value_percentage > 10) return 'bg-green-500/20 border-green-500/50';
    if (vb.is_value_bet && vb.value_percentage > 5) return 'bg-yellow-500/20 border-yellow-500/50';
    if (vb.is_value_bet) return 'bg-orange-500/20 border-orange-500/50';
    return 'bg-slate-800/50 border-slate-700';
  };

  return (
    <div className="rounded-2xl bg-gradient-to-br from-amber-600/10 to-orange-600/10 border border-amber-500/30 p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <span className="text-3xl">🎰</span>
          <div>
            <h3 className="font-bold text-xl text-amber-400">Cotes de Paris</h3>
            <p className="text-xs text-slate-400">The Odds API - Analyse Value Bet</p>
          </div>
        </div>
        
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="px-4 py-2 rounded-lg bg-amber-500/20 text-amber-400 border border-amber-500/50 hover:bg-amber-500/30 transition-all text-sm font-medium disabled:opacity-50"
        >
          {refreshing ? 'Chargement...' : '🔄 Rafraîchir'}
        </button>
      </div>

      {hasOdds ? (
        <>
          <div className="grid grid-cols-3 gap-4 mb-6">
            {/* Victoire Domicile */}
            <div className={`relative rounded-xl p-4 border transition-all ${getValueBg(valueBets.home)}`}>
              <div className="text-center">
                <p className="text-xs text-slate-400 mb-1">1 - Domicile</p>
                <p className="text-3xl font-black text-white mb-2">{odds.home?.toFixed(2) || '-'}</p>
                {odds.home && <p className="text-xs text-slate-500">{impliedProb(odds.home)}%</p>}
                {valueBets.home && (
                  <p className={`text-sm font-bold mt-2 ${getValueColor(valueBets.home)}`}>
                    {valueBets.home.value_percentage > 0 ? '+' : ''}{valueBets.home.value_percentage.toFixed(1)}%
                  </p>
                )}
              </div>
            </div>

            {/* Match Nul */}
            <div className={`relative rounded-xl p-4 border transition-all ${getValueBg(valueBets.draw)}`}>
              <div className="text-center">
                <p className="text-xs text-slate-400 mb-1">X - Nul</p>
                <p className="text-3xl font-black text-white mb-2">{odds.draw?.toFixed(2) || '-'}</p>
                {odds.draw && <p className="text-xs text-slate-500">{impliedProb(odds.draw)}%</p>}
                {valueBets.draw && (
                  <p className={`text-sm font-bold mt-2 ${getValueColor(valueBets.draw)}`}>
                    {valueBets.draw.value_percentage > 0 ? '+' : ''}{valueBets.draw.value_percentage.toFixed(1)}%
                  </p>
                )}
              </div>
            </div>

            {/* Victoire Extérieur */}
            <div className={`relative rounded-xl p-4 border transition-all ${getValueBg(valueBets.away)}`}>
              <div className="text-center">
                <p className="text-xs text-slate-400 mb-1">2 - Extérieur</p>
                <p className="text-3xl font-black text-white mb-2">{odds.away?.toFixed(2) || '-'}</p>
                {odds.away && <p className="text-xs text-slate-500">{impliedProb(odds.away)}%</p>}
                {valueBets.away && (
                  <p className={`text-sm font-bold mt-2 ${getValueColor(valueBets.away)}`}>
                    {valueBets.away.value_percentage > 0 ? '+' : ''}{valueBets.away.value_percentage.toFixed(1)}%
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Recommandations */}
          {Object.entries(valueBets).some(([type, vb]) => vb.is_value_bet && type) && (
            <div className="rounded-xl bg-slate-900/50 border border-green-500/30 p-4">
              <h4 className="font-bold text-green-400 mb-2 flex items-center gap-2">🔥 Opportunités trouvées</h4>
              <div className="space-y-2">
                {Object.entries(valueBets).filter(([type, vb]) => vb.is_value_bet && type).map(([type, vb]) => (
                  <div key={type} className="flex justify-between items-center text-sm p-2 bg-slate-800/50 rounded">
                    <span className="text-slate-200">
                      {type === 'home' ? match.home_team : type === 'away' ? match.away_team : 'Match Nul'}
                    </span>
                    <span className="font-bold text-green-400">EV: +{(vb.expected_value * 100).toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-8">
          <p className="text-slate-400 mb-4 text-sm">Aucune cote disponible pour ce match.</p>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="px-6 py-2 rounded-xl bg-amber-500/20 text-amber-400 border border-amber-500/50 hover:bg-amber-500/30 transition-all"
          >
            {refreshing ? 'Chargement...' : '🔍 Chercher les cotes'}
          </button>
        </div>
      )}
    </div>
  );
}
