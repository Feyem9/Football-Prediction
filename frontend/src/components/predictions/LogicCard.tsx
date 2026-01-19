/**
 * LogicCard Component - Affiche une logique avec ses preuves
 */
interface LogicEvidence {
  // Papa
  home_position?: number;
  away_position?: number;
  home_points?: number;
  away_points?: number;
  league_level?: number;
  // Grand Frère
  home_advantage?: number;
  home_strength?: string;
  away_strength?: string;
  h2h_home_wins?: number;
  h2h_away_wins?: number;
  h2h_draws?: number;
  // Ma Logique
  home_form?: number;
  away_form?: number;
  home_avg_goals?: number;
  away_avg_goals?: number;
}

interface LogicPrediction {
  home_win_prob: number;
  draw_prob: number;
  away_win_prob: number;
  predicted_home_goals: number;
  predicted_away_goals: number;
  confidence: number;
  bet_tip: string;
  analysis: string;
}

interface LogicCardProps {
  name: 'papa' | 'grand_frere' | 'ma_logique';
  prediction: LogicPrediction | null;
  evidence?: LogicEvidence;
  homeTeam: string;
  awayTeam: string;
}

const CONFIG = {
  papa: {
    emoji: '🟢',
    title: 'Papa',
    color: 'green',
    gradient: 'from-green-600/20 to-emerald-600/20',
    border: 'border-green-500/50',
    text: 'text-green-400',
  },
  grand_frere: {
    emoji: '🔵',
    title: 'Grand Frère',
    color: 'blue',
    gradient: 'from-blue-600/20 to-cyan-600/20',
    border: 'border-blue-500/50',
    text: 'text-blue-400',
  },
  ma_logique: {
    emoji: '🟣',
    title: 'Ma Logique',
    color: 'purple',
    gradient: 'from-purple-600/20 to-pink-600/20',
    border: 'border-purple-500/50',
    text: 'text-purple-400',
  },
};

export default function LogicCard({ name, prediction, evidence, homeTeam, awayTeam }: LogicCardProps) {
  const config = CONFIG[name];
  
  if (!prediction) {
    return (
      <div className={`rounded-2xl bg-gradient-to-br ${config.gradient} border ${config.border} p-5 opacity-50`}>
        <div className="flex items-center gap-2 mb-3">
          <span className="text-2xl">{config.emoji}</span>
          <span className={`font-bold ${config.text}`}>{config.title}</span>
        </div>
        <p className="text-slate-500 text-sm">Données insuffisantes</p>
      </div>
    );
  }

  return (
    <div className={`rounded-2xl bg-gradient-to-br ${config.gradient} border ${config.border} p-5 hover:scale-[1.02] transition-all`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{config.emoji}</span>
          <span className={`font-bold text-lg ${config.text}`}>{config.title}</span>
        </div>
        <span className="text-sm text-slate-400">{Math.round(prediction.confidence * 100)}%</span>
      </div>

      {/* Score Prédit */}
      <div className="text-center mb-4">
        <div className="inline-flex items-center gap-3 px-6 py-3 rounded-xl bg-slate-900/50">
          <span className="text-3xl font-black text-white">{prediction.predicted_home_goals}</span>
          <span className="text-xl text-slate-500">-</span>
          <span className="text-3xl font-black text-white">{prediction.predicted_away_goals}</span>
        </div>
      </div>

      {/* Conseil */}
      <div className="text-center mb-4">
        <span className={`inline-block px-4 py-1.5 rounded-full text-sm font-bold ${config.gradient} ${config.text} border ${config.border}`}>
          {prediction.bet_tip}
        </span>
      </div>

      {/* PREUVES / ÉVIDENCES */}
      <div className="space-y-2 pt-4 border-t border-slate-700/50">
        <p className="text-xs text-slate-500 uppercase tracking-wide mb-2">📊 Preuves</p>
        
        {name === 'papa' && evidence && (
          <>
            <EvidenceRow 
              label={homeTeam} 
              value={`#${evidence.home_position} (${evidence.home_points} pts)`} 
            />
            <EvidenceRow 
              label={awayTeam} 
              value={`#${evidence.away_position} (${evidence.away_points} pts)`} 
            />
            <EvidenceRow 
              label="Niveau Ligue" 
              value={`${Math.round((evidence.league_level || 0) * 100)}%`}
              highlight
            />
          </>
        )}
        
        {name === 'grand_frere' && evidence && (
          <>
            <EvidenceRow 
              label="Force Domicile" 
              value={evidence.home_strength || 'MOYEN'} 
            />
            <EvidenceRow 
              label="Force Extérieur" 
              value={evidence.away_strength || 'MOYEN'} 
            />
            <EvidenceRow 
              label="Avantage Domicile" 
              value={`${Math.round((evidence.home_advantage || 0) * 100)}%`}
              highlight
            />
            {(evidence.h2h_home_wins !== undefined) && (
              <EvidenceRow 
                label="H2H" 
                value={`${evidence.h2h_home_wins}V - ${evidence.h2h_draws}N - ${evidence.h2h_away_wins}D`} 
              />
            )}
          </>
        )}
        
        {name === 'ma_logique' && evidence && (
          <>
            <EvidenceRow 
              label="Forme Domicile" 
              value={`${Math.round((evidence.home_form || 0) * 100)}%`} 
            />
            <EvidenceRow 
              label="Forme Extérieur" 
              value={`${Math.round((evidence.away_form || 0) * 100)}%`} 
            />
            <EvidenceRow 
              label="Moy. Buts Dom." 
              value={`${(evidence.home_avg_goals || 0).toFixed(1)}`}
              highlight
            />
            <EvidenceRow 
              label="Moy. Buts Ext." 
              value={`${(evidence.away_avg_goals || 0).toFixed(1)}`}
            />
          </>
        )}
      </div>

      {/* Analyse textuelle */}
      <p className="text-xs text-slate-400 mt-4 italic">
        "{prediction.analysis}"
      </p>
    </div>
  );
}

function EvidenceRow({ label, value, highlight = false }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className="flex justify-between items-center text-sm">
      <span className="text-slate-400">{label}</span>
      <span className={highlight ? 'font-bold text-white' : 'text-slate-300'}>{value}</span>
    </div>
  );
}
