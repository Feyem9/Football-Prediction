/**
 * PredictionCard Component - Affiche les 3 logiques de prédiction
 */
import type { CombinedPrediction, LogicPrediction } from '../types';

interface PredictionCardProps {
  prediction: CombinedPrediction;
}

function LogicBox({ 
  name, 
  emoji, 
  logic, 
  color 
}: { 
  name: string; 
  emoji: string; 
  logic: LogicPrediction | null; 
  color: string;
}) {
  if (!logic) return null;
  
  return (
    <div className={`bg-slate-800/80 rounded-xl p-4 border ${color}`}>
      <div className="flex items-center gap-2 mb-3">
        <span className="text-xl">{emoji}</span>
        <span className="font-semibold text-white">{name}</span>
        <span className="ml-auto text-sm text-slate-400">
          {Math.round(logic.confidence * 100)}%
        </span>
      </div>
      
      <div className="text-center mb-3">
        <span className="text-2xl font-bold text-white">
          {logic.predicted_home_goals} - {logic.predicted_away_goals}
        </span>
      </div>
      
      <div className="text-center">
        <span className={`text-sm px-3 py-1 rounded-full ${color.replace('border-', 'bg-').replace('500', '900/50')} ${color.replace('border-', 'text-').replace('500', '400')}`}>
          {logic.bet_tip}
        </span>
      </div>
      
      <p className="text-xs text-slate-400 mt-3 line-clamp-2">
        {logic.analysis}
      </p>
    </div>
  );
}

export default function PredictionCard({ prediction }: PredictionCardProps) {
  const consensusColors = {
    FORT: 'text-green-400 bg-green-900/50 border-green-500',
    MOYEN: 'text-yellow-400 bg-yellow-900/50 border-yellow-500',
    FAIBLE: 'text-red-400 bg-red-900/50 border-red-500',
  };
  
  const consensusEmoji = {
    FORT: '🟢',
    MOYEN: '🟡',
    FAIBLE: '🔴',
  };

  return (
    <div className="space-y-6">
      {/* Final Prediction */}
      <div className="bg-gradient-to-r from-blue-900/50 to-purple-900/50 rounded-xl p-6 border border-blue-500">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">🎯 Prédiction Finale</h3>
          <span className={`px-3 py-1 rounded-full text-sm border ${consensusColors[prediction.consensus_level]}`}>
            {consensusEmoji[prediction.consensus_level]} Consensus {prediction.consensus_level}
          </span>
        </div>
        
        <div className="flex items-center justify-center gap-8 mb-4">
          <div className="text-center">
            <p className="text-slate-400 text-sm mb-1">{prediction.home_team}</p>
            <span className="text-4xl font-bold text-white">{prediction.final_home_goals}</span>
          </div>
          <span className="text-2xl text-slate-500">-</span>
          <div className="text-center">
            <p className="text-slate-400 text-sm mb-1">{prediction.away_team}</p>
            <span className="text-4xl font-bold text-white">{prediction.final_away_goals}</span>
          </div>
        </div>
        
        <div className="flex items-center justify-center gap-4">
          <span className="bg-blue-500 text-white px-4 py-2 rounded-lg font-semibold">
            💡 {prediction.final_bet_tip}
          </span>
          <span className="text-slate-400">
            Confiance: {Math.round(prediction.final_confidence * 100)}%
          </span>
        </div>
      </div>

      {/* Three Logics */}
      <div className="grid md:grid-cols-3 gap-4">
        <LogicBox 
          name="Papa" 
          emoji="🟢" 
          logic={prediction.papa_prediction} 
          color="border-green-500"
        />
        <LogicBox 
          name="Grand Frère" 
          emoji="🔵" 
          logic={prediction.grand_frere_prediction} 
          color="border-blue-500"
        />
        <LogicBox 
          name="Ma Logique" 
          emoji="🟣" 
          logic={prediction.ma_logique_prediction} 
          color="border-purple-500"
        />
      </div>
    </div>
  );
}
