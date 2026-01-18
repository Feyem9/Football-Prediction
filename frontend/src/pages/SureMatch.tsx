/**
 * SureMatch Page - Match Sûr du Jour
 * Affiche le match le plus fiable avec toutes les explications
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getMatches, getCombinedPrediction } from '../lib/api';
import type { Match, CombinedPrediction, LogicPrediction } from '../types';

export default function SureMatch() {
  const [sureMatch, setSureMatch] = useState<Match | null>(null);
  const [prediction, setPrediction] = useState<CombinedPrediction | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSureMatch = async () => {
      try {
        // Récupérer tous les matchs à venir
        const data = await getMatches({ limit: 50 });
        
        // Trouver le match avec la plus haute confiance
        let bestMatch: Match | null = null;
        let bestConfidence = 0;
        
        for (const match of data.matches) {
          const conf = match.prediction?.confidence || 0;
          if (conf > bestConfidence) {
            bestConfidence = conf;
            bestMatch = match;
          }
        }
        
        if (bestMatch) {
          setSureMatch(bestMatch);
          
          // Récupérer la prédiction détaillée
          const pred = await getCombinedPrediction(bestMatch.id);
          setPrediction(pred);
        }
      } catch (err) {
        setError('Erreur lors du chargement');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchSureMatch();
  }, []);

  const today = new Date().toLocaleDateString('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });

  // Critères de sélection du match sûr
  const getSurenessCriteria = () => {
    if (!prediction || !sureMatch) return [];
    
    const criteria = [];
    const pred = sureMatch.prediction;
    const conf = pred?.confidence || 0;
    
    // Critère 1: Confiance élevée
    if (conf >= 0.7) {
      criteria.push({
        icon: '✅',
        title: 'Confiance Élevée',
        description: `Score de confiance de ${Math.round(conf * 100)}% - Supérieur au seuil de 70%`,
        score: conf
      });
    }
    
    // Critère 2: Consensus des logiques
    if (prediction.all_agree) {
      criteria.push({
        icon: '🤝',
        title: 'Consensus Total',
        description: 'Les 3 logiques familiales sont d\'accord sur le résultat',
        score: 1
      });
    } else if (prediction.consensus_level === 'FORT') {
      criteria.push({
        icon: '📊',
        title: 'Consensus Fort',
        description: '2 logiques sur 3 sont d\'accord',
        score: 0.8
      });
    }
    
    // Critère 3: Différence de niveau
    const papaEvidence = prediction.papa_prediction?.evidence;
    if (papaEvidence) {
      const homePos = papaEvidence.home_position || 10;
      const awayPos = papaEvidence.away_position || 10;
      const posDiff = Math.abs(homePos - awayPos);
      if (posDiff >= 8) {
        criteria.push({
          icon: '📈',
          title: 'Grande Différence de Classement',
          description: `${posDiff} places d'écart au classement`,
          score: posDiff / 20
        });
      }
    }
    
    // Critère 4: Avantage domicile fort
    const gfEvidence = prediction.grand_frere_prediction?.evidence;
    if (gfEvidence && gfEvidence.home_advantage && gfEvidence.home_advantage > 0.15) {
      criteria.push({
        icon: '🏠',
        title: 'Fort Avantage Domicile',
        description: `Bonus domicile de ${Math.round((gfEvidence.home_advantage || 0) * 100)}%`,
        score: gfEvidence.home_advantage
      });
    }
    
    // Critère 5: Forme récente
    const maLogiqueEvidence = prediction.ma_logique_prediction?.evidence;
    if (maLogiqueEvidence) {
      const homeForm = maLogiqueEvidence.home_form || 0.5;
      const awayForm = maLogiqueEvidence.away_form || 0.5;
      const formDiff = Math.abs(homeForm - awayForm);
      if (formDiff > 0.3) {
        criteria.push({
          icon: '🔥',
          title: 'Grande Différence de Forme',
          description: `Écart de forme significatif: ${Math.round(formDiff * 100)}%`,
          score: formDiff
        });
      }
    }
    
    return criteria;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-yellow-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-400">Analyse des matchs en cours...</p>
        </div>
      </div>
    );
  }

  if (error || !sureMatch) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <span className="text-6xl mb-4 block">😔</span>
          <p className="text-red-400">{error || 'Aucun match sûr trouvé'}</p>
          <Link to="/" className="mt-4 inline-block px-6 py-3 rounded-xl bg-blue-500 text-white">
            Retour à l'accueil
          </Link>
        </div>
      </div>
    );
  }

  const criteria = getSurenessCriteria();
  const pred = sureMatch.prediction;
  const matchDate = new Date(sureMatch.match_date).toLocaleDateString('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    hour: '2-digit',
    minute: '2-digit'
  });

  return (
    <div className="min-h-screen pb-16">
      {/* Hero */}
      <div className="relative py-12 mb-8">
        <div className="absolute inset-0 bg-gradient-to-r from-yellow-600/20 via-amber-600/10 to-transparent" />
        <div className="relative container mx-auto px-4 text-center">
          <span className="text-5xl mb-4 block">🎯</span>
          <h1 className="text-3xl md:text-5xl font-black text-white mb-2">
            Match <span className="text-yellow-400">Sûr</span> du Jour
          </h1>
          <p className="text-slate-400 capitalize">{today}</p>
        </div>
      </div>

      <div className="container mx-auto px-4 max-w-4xl">
        {/* Match Card Principal */}
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-yellow-900/30 via-slate-900 to-slate-900 border-2 border-yellow-500/50 p-8 mb-8">
          {/* Badge Confiance */}
          <div className="absolute top-4 right-4">
            <div className="px-4 py-2 rounded-full bg-yellow-500 text-black font-black text-lg">
              {Math.round((pred?.confidence || 0) * 100)}% SÛR
            </div>
          </div>

          {/* Compétition */}
          <div className="text-center mb-6">
            <span className="text-sm font-bold px-4 py-2 rounded-full bg-slate-700 text-slate-300">
              {sureMatch.competition_name} • J{sureMatch.matchday}
            </span>
            <p className="text-slate-500 text-sm mt-2">{matchDate}</p>
          </div>

          {/* Teams & Score */}
          <div className="flex items-center justify-center gap-8 mb-8">
            <div className="text-center flex-1">
              <p className="text-2xl md:text-3xl font-black text-white">
                {sureMatch.home_team}
              </p>
              <p className="text-slate-500 text-sm">Domicile</p>
            </div>

            <div className="flex items-center gap-4 px-8 py-4 rounded-2xl bg-yellow-500/20 border-2 border-yellow-500/50">
              <span className="text-5xl font-black text-yellow-400">{pred?.home_score_forecast}</span>
              <span className="text-3xl text-yellow-300">-</span>
              <span className="text-5xl font-black text-yellow-400">{pred?.away_score_forecast}</span>
            </div>

            <div className="text-center flex-1">
              <p className="text-2xl md:text-3xl font-black text-white">
                {sureMatch.away_team}
              </p>
              <p className="text-slate-500 text-sm">Extérieur</p>
            </div>
          </div>

          {/* Conseil */}
          <div className="text-center">
            <span className="text-2xl font-bold text-yellow-400">
              🎯 {pred?.bet_tip}
            </span>
          </div>
        </div>

        {/* Pourquoi ce match est sûr */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
            <span className="text-3xl">🔍</span>
            Pourquoi ce match est SÛR ?
          </h2>

          <div className="grid gap-4">
            {criteria.map((c, i) => (
              <div 
                key={i}
                className="p-5 rounded-2xl bg-slate-800/70 border border-slate-700 hover:border-yellow-500/50 transition-colors"
              >
                <div className="flex items-start gap-4">
                  <span className="text-3xl">{c.icon}</span>
                  <div className="flex-1">
                    <h3 className="font-bold text-yellow-400 text-lg">{c.title}</h3>
                    <p className="text-slate-400">{c.description}</p>
                  </div>
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 rounded-full bg-yellow-500/20 flex items-center justify-center">
                      <span className="text-yellow-400 font-bold">
                        {Math.round(c.score * 100)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Analyse des 3 Logiques */}
        {prediction && (
          <section className="mb-8">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
              <span className="text-3xl">🧠</span>
              Analyse des 3 Logiques Familiales
            </h2>

            <div className="grid md:grid-cols-3 gap-4">
              {/* Papa */}
              {prediction.papa_prediction && (
                <LogicCard 
                  name="Papa"
                  color="green"
                  icon="👨"
                  prediction={prediction.papa_prediction}
                  confidence={prediction.papa_prediction.confidence}
                />
              )}

              {/* Grand Frère */}
              {prediction.grand_frere_prediction && (
                <LogicCard 
                  name="Grand Frère"
                  color="blue"
                  icon="👦"
                  prediction={prediction.grand_frere_prediction}
                  confidence={prediction.grand_frere_prediction.confidence}
                />
              )}

              {/* Ma Logique */}
              {prediction.ma_logique_prediction && (
                <LogicCard 
                  name="Ma Logique"
                  color="purple"
                  icon="🧠"
                  prediction={prediction.ma_logique_prediction}
                  confidence={prediction.ma_logique_prediction.confidence}
                />
              )}
            </div>

            {/* Consensus */}
            <div className="mt-6 p-6 rounded-2xl bg-slate-800/70 border border-yellow-500/50">
              <div className="flex items-center gap-4">
                <span className="text-4xl">
                  {prediction.all_agree ? '🤝' : prediction.consensus_level === 'FORT' ? '📊' : '⚖️'}
                </span>
                <div>
                  <h3 className="font-bold text-yellow-400 text-lg">
                    Consensus: {prediction.consensus_level}
                  </h3>
                  <p className="text-slate-400">
                    {prediction.all_agree 
                      ? 'Les 3 logiques sont unanimes sur le résultat !'
                      : prediction.consensus_level === 'FORT'
                        ? '2 logiques sur 3 sont d\'accord'
                        : 'Les logiques divergent légèrement'
                    }
                  </p>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Lien vers détail */}
        <div className="text-center">
          <Link 
            to={`/matches/${sureMatch.id}`}
            className="inline-block px-8 py-4 rounded-2xl bg-yellow-500 text-black font-bold text-lg hover:bg-yellow-400 transition-colors"
          >
            Voir l'analyse complète →
          </Link>
        </div>
      </div>
    </div>
  );
}

/**
 * LogicCard - Carte pour afficher une logique
 */
function LogicCard({ 
  name, 
  color, 
  icon, 
  prediction,
  confidence 
}: { 
  name: string;
  color: 'green' | 'blue' | 'purple';
  icon: string;
  prediction: LogicPrediction;
  confidence: number;
}) {
  const colorClasses = {
    green: 'from-green-900/50 border-green-500/50 text-green-400',
    blue: 'from-blue-900/50 border-blue-500/50 text-blue-400',
    purple: 'from-purple-900/50 border-purple-500/50 text-purple-400'
  };

  return (
    <div className={`p-5 rounded-2xl bg-gradient-to-br ${colorClasses[color]} to-slate-900 border`}>
      <div className="flex items-center gap-3 mb-4">
        <span className="text-2xl">{icon}</span>
        <h3 className="font-bold text-lg">{name}</h3>
        <span className="ml-auto text-sm bg-slate-800 px-3 py-1 rounded-full">
          {Math.round(confidence * 100)}%
        </span>
      </div>

      <div className="text-center mb-4">
        <span className="text-3xl font-black text-white">
          {prediction.predicted_home_goals} - {prediction.predicted_away_goals}
        </span>
      </div>

      <p className="text-sm text-slate-400">
        {prediction.bet_tip?.split(' - ')[0]}
      </p>

      {/* Evidence mini */}
      {prediction.evidence && (
        <div className="mt-3 pt-3 border-t border-slate-700/50 text-xs text-slate-500">
          {prediction.evidence.home_position && (
            <p>Position: #{prediction.evidence.home_position} vs #{prediction.evidence.away_position}</p>
          )}
          {prediction.evidence.home_form !== undefined && (
            <p>Forme: {Math.round(prediction.evidence.home_form * 100)}% vs {Math.round(prediction.evidence.away_form * 100)}%</p>
          )}
        </div>
      )}
    </div>
  );
}
