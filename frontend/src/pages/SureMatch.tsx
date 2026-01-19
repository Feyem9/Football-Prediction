/**
 * SureMatch Page - Matchs Sûrs du Jour
 * Affiche 4 catégories de matchs sûrs avec explications simples
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getMatches, getCombinedPrediction } from '../lib/api';
import type { Match, CombinedPrediction, LogicPrediction } from '../types';

interface SureMatchCategory {
  type: 'victory' | 'goals' | 'draw' | 'exact';
  title: string;
  icon: string;
  match: Match | null;
  prediction: CombinedPrediction | null;
  explanation: string;
}

export default function SureMatch() {
  const [categories, setCategories] = useState<SureMatchCategory[]>([
    { type: 'victory', title: 'Victoire Sûre', icon: '🏆', match: null, prediction: null, explanation: '' },
    { type: 'goals', title: 'Nombre de Buts', icon: '⚽', match: null, prediction: null, explanation: '' },
    { type: 'draw', title: 'Match Nul', icon: '🤝', match: null, prediction: null, explanation: '' },
    { type: 'exact', title: 'Score Exact', icon: '🎯', match: null, prediction: null, explanation: '' },
  ]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'victory' | 'goals' | 'draw' | 'exact'>('victory');

  useEffect(() => {
    const fetchSureMatches = async () => {
      try {
        const data = await getMatches({ limit: 50 });
        console.log('📊 Matchs reçus:', data.matches.length, data.matches.slice(0, 3));
        
        // Créer les catégories localement pour éviter le warning eslint
        const newCategories: SureMatchCategory[] = [
          { type: 'victory', title: 'Victoire Sûre', icon: '🏆', match: null, prediction: null, explanation: '' },
          { type: 'goals', title: 'Nombre de Buts', icon: '⚽', match: null, prediction: null, explanation: '' },
          { type: 'draw', title: 'Match Nul', icon: '🤝', match: null, prediction: null, explanation: '' },
          { type: 'exact', title: 'Score Exact', icon: '🎯', match: null, prediction: null, explanation: '' },
        ];
        
        for (const match of data.matches) {
          const conf = match.prediction?.confidence || 0;
          const tip = match.prediction?.bet_tip || '';
          const homeScore = match.prediction?.home_score_forecast ?? 0;
          const awayScore = match.prediction?.away_score_forecast ?? 0;
          
          // Victoire Sûre - Match avec victoire claire
          if (tip.includes('Victoire') && conf > 0.75) {
            const cat = newCategories.find(c => c.type === 'victory');
            if (cat && (!cat.match || conf > (cat.match.prediction?.confidence || 0))) {
              cat.match = match;
            }
          }
          
          // Nombre de Buts - Plus/Moins 2.5
          if ((tip.includes('Plus de 2.5') || tip.includes('Moins de 2.5')) && conf > 0.6) {
            const cat = newCategories.find(c => c.type === 'goals');
            if (cat && (!cat.match || conf > (cat.match.prediction?.confidence || 0))) {
              cat.match = match;
            }
          }
          
          // Match Nul - homeScore === awayScore
          if (homeScore === awayScore && conf > 0.5) {
            const cat = newCategories.find(c => c.type === 'draw');
            if (cat && (!cat.match || conf > (cat.match.prediction?.confidence || 0))) {
              cat.match = match;
            }
          }
          
          // Score Exact - Haute confiance
          if (conf > 0.8) {
            const cat = newCategories.find(c => c.type === 'exact');
            if (cat && (!cat.match || conf > (cat.match.prediction?.confidence || 0))) {
              cat.match = match;
            }
          }
        }
        
        // Debug: afficher les matchs trouvés
        console.log('🏆 Catégories après sélection:', newCategories.map(c => ({
          type: c.type,
          hasMatch: !!c.match,
          matchName: c.match ? `${c.match.home_team} vs ${c.match.away_team}` : null
        })));
        
        // Récupérer les prédictions détaillées
        for (const cat of newCategories) {
          if (cat.match) {
            try {
              cat.prediction = await getCombinedPrediction(cat.match.id);
              console.log(`✅ Prediction loaded for ${cat.type}`);
            } catch (err) {
              console.error(`❌ Error loading prediction for ${cat.type}:`, err);
            }
          }
        }
        
        setCategories(newCategories);
      } catch (err) {
        console.error('❌ Erreur globale:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchSureMatches();
  }, []);

  const today = new Date().toLocaleDateString('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });

  const activeCategory = categories.find(c => c.type === activeTab);

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

  return (
    <div className="min-h-screen pb-16">
      {/* Hero */}
      <div className="relative py-12 mb-8">
        <div className="absolute inset-0 bg-gradient-to-r from-yellow-600/20 via-amber-600/10 to-transparent" />
        <div className="relative container mx-auto px-4 text-center">
          <span className="text-5xl mb-4 block">🎯</span>
          <h1 className="text-3xl md:text-5xl font-black text-white mb-2">
            Matchs <span className="text-yellow-400">Sûrs</span> du Jour
          </h1>
          <p className="text-slate-400 capitalize">{today}</p>
        </div>
      </div>

      <div className="container mx-auto px-4 max-w-5xl">
        {/* Tabs - 4 catégories */}
        <div className="flex flex-wrap justify-center gap-2 mb-8">
          {categories.map(cat => (
            <button
              key={cat.type}
              onClick={() => setActiveTab(cat.type)}
              className={`px-6 py-3 rounded-xl font-bold transition-all ${
                activeTab === cat.type
                  ? 'bg-yellow-500 text-black scale-105'
                  : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
              }`}
            >
              <span className="mr-2">{cat.icon}</span>
              {cat.title}
            </button>
          ))}
        </div>

        {/* Contenu de la catégorie active */}
        {activeCategory?.match ? (
          <SureMatchCard 
            category={activeCategory} 
          />
        ) : (
          <div className="text-center py-12 bg-slate-800/50 rounded-3xl">
            <span className="text-6xl mb-4 block">🔍</span>
            <p className="text-slate-400">Aucun match sûr trouvé pour cette catégorie</p>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * SureMatchCard - Carte complète avec explications
 */
function SureMatchCard({ category }: { category: SureMatchCategory }) {
  const { match, prediction, title, icon } = category;
  
  if (!match) return null;
  
  const pred = match.prediction;
  const matchDate = new Date(match.match_date).toLocaleDateString('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    hour: '2-digit',
    minute: '2-digit'
  });

  return (
    <div className="space-y-8">
      {/* Match Card */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-yellow-900/30 via-slate-900 to-slate-900 border-2 border-yellow-500/50 p-8">
        <div className="absolute top-4 right-4">
          <div className="px-4 py-2 rounded-full bg-yellow-500 text-black font-black text-lg">
            {Math.round((pred?.confidence || 0) * 100)}% SÛR
          </div>
        </div>

        <div className="text-center mb-4">
          <span className="text-3xl">{icon}</span>
          <span className="text-xl font-bold text-yellow-400 ml-2">{title}</span>
        </div>

        <div className="text-center mb-4">
          <span className="text-sm font-bold px-4 py-2 rounded-full bg-slate-700 text-slate-300">
            {match.competition_name} • J{match.matchday}
          </span>
          <p className="text-slate-500 text-sm mt-2">{matchDate}</p>
        </div>

        <div className="flex items-center justify-center gap-8 mb-6">
          <div className="text-center flex-1">
            <p className="text-2xl md:text-3xl font-black text-white">{match.home_team}</p>
            <p className="text-slate-500 text-sm">Domicile</p>
          </div>

          <div className="flex items-center gap-4 px-8 py-4 rounded-2xl bg-yellow-500/20 border-2 border-yellow-500/50">
            <span className="text-5xl font-black text-yellow-400">{pred?.home_score_forecast}</span>
            <span className="text-3xl text-yellow-300">-</span>
            <span className="text-5xl font-black text-yellow-400">{pred?.away_score_forecast}</span>
          </div>

          <div className="text-center flex-1">
            <p className="text-2xl md:text-3xl font-black text-white">{match.away_team}</p>
            <p className="text-slate-500 text-sm">Extérieur</p>
          </div>
        </div>

        <div className="text-center">
          <span className="text-2xl font-bold text-yellow-400">🎯 {pred?.bet_tip}</span>
        </div>
      </div>

      {/* Explications simples des 3 logiques */}
      {prediction && (
        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-white text-center">
            📚 Comment on a trouvé ce match sûr ?
          </h2>

          {/* Ma Logique */}
          <LogicExplanation
            name="Ma Logique"
            icon="🧠"
            color="purple"
            shortExplanation={`C'est comme regarder comment les équipes jouent ces derniers temps. Imagine que tu regardes les 10 derniers matchs. Si une équipe gagne beaucoup, elle est "en forme", comme quand tu joues bien à un jeu vidéo parce que tu t'es entraîné !`}
            data={prediction.ma_logique_prediction}
            getDetails={(p) => {
              const ev = p.evidence;
              return [
                { label: 'Forme de l\'équipe à domicile', value: `${Math.round((ev?.home_form ?? 0.5) * 100)}%` },
                { label: 'Forme de l\'équipe extérieur', value: `${Math.round((ev?.away_form ?? 0.5) * 100)}%` },
                { label: 'Buts moyens marqués domicile', value: `${(ev?.home_avg_goals ?? 1.3).toFixed(1)} par match` },
                { label: 'Buts moyens marqués extérieur', value: `${(ev?.away_avg_goals ?? 1.2).toFixed(1)} par match` },
              ];
            }}
          />

          {/* Logique de Papa */}
          <LogicExplanation
            name="Logique de Papa"
            icon="👨"
            color="green"
            shortExplanation={`Papa regarde le classement et les points. C'est comme à l'école : si tu es 1er de la classe avec plein de bons points, tu es probablement meilleur qu'un élève qui est 15ème. Papa regarde aussi le niveau du championnat - la Premier League c'est comme le concours des meilleurs, la Ligue 1 c'est un cran en dessous.`}
            data={prediction.papa_prediction}
            getDetails={(p) => {
              const ev = p.evidence;
              return [
                { label: 'Position au classement domicile', value: `#${ev?.home_position ?? '?'}` },
                { label: 'Position au classement extérieur', value: `#${ev?.away_position ?? '?'}` },
                { label: 'Points domicile', value: `${ev?.home_points ?? '?'} pts` },
                { label: 'Points extérieur', value: `${ev?.away_points ?? '?'} pts` },
                { label: 'Niveau du championnat', value: ev?.league_level ? `${Math.round((ev.league_level as number) * 100)}%` : '?' },
              ];
            }}
          />

          {/* Logique de Grand Frère */}
          <LogicExplanation
            name="Logique de Grand Frère"
            icon="👦"
            color="blue"
            shortExplanation={`Grand frère a une règle d'or : "Jouer à la maison, c'est un super pouvoir !" C'est comme quand tu joues à un jeu chez toi - tu connais le terrain, tes parents t'encouragent. On regarde aussi les matchs précédents entre ces équipes (H2H = Head to Head). Si une équipe gagne toujours contre l'autre, c'est comme un grand frère qui bat toujours son petit frère au foot !`}
            data={prediction.grand_frere_prediction}
            getDetails={(p) => {
              const ev = p.evidence;
              return [
                { label: 'Avantage à domicile', value: ev?.home_advantage ? `+${Math.round((ev.home_advantage as number) * 100)}%` : '+12%' },
                { label: 'Force équipe domicile', value: ev?.home_strength ?? '?' },
                { label: 'Force équipe extérieur', value: ev?.away_strength ?? '?' },
                { label: 'Historique H2H', value: ev?.h2h_home_wins !== undefined ? `${ev.h2h_home_wins}V - ${ev.h2h_draws ?? 0}N - ${ev.h2h_away_wins ?? 0}D` : 'Pas assez de données' },
              ];
            }}
          />

          {/* Résumé Consensus */}
          <div className="p-6 rounded-3xl bg-gradient-to-br from-yellow-900/30 to-slate-900 border-2 border-yellow-500/50">
            <div className="flex items-center gap-4 mb-4">
              <span className="text-4xl">{prediction.all_agree ? '🎉' : '🤔'}</span>
              <div>
                <h3 className="text-xl font-bold text-yellow-400">
                  Résultat Final : {prediction.all_agree ? 'TOUS D\'ACCORD !' : 'Consensus ' + prediction.consensus_level}
                </h3>
                <p className="text-slate-400">
                  {prediction.all_agree 
                    ? 'Les 3 logiques (Moi, Papa et Grand Frère) ont toutes prédit la même chose. C\'est super rare et très fiable !'
                    : `${prediction.consensus_level === 'FORT' ? '2 logiques sur 3' : 'Les logiques'} sont ${prediction.consensus_level === 'FORT' ? 'd\'accord' : 'partagées'}. On prend la moyenne de leurs avis.`
                  }
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Lien vers détail */}
      <div className="text-center">
        <Link 
          to={`/matches/${match.id}`}
          className="inline-block px-8 py-4 rounded-2xl bg-yellow-500 text-black font-bold text-lg hover:bg-yellow-400 transition-colors"
        >
          Voir l'analyse complète →
        </Link>
      </div>
    </div>
  );
}

/**
 * LogicExplanation - Explication simple d'une logique
 */
function LogicExplanation({ 
  name, 
  icon, 
  color, 
  shortExplanation,
  data,
  getDetails
}: { 
  name: string;
  icon: string;
  color: 'green' | 'blue' | 'purple';
  shortExplanation: string;
  data: LogicPrediction | null | undefined;
  getDetails: (p: LogicPrediction) => { label: string; value: string }[];
}) {
  const colorClasses = {
    green: 'from-green-900/40 border-green-500/50',
    blue: 'from-blue-900/40 border-blue-500/50',
    purple: 'from-purple-900/40 border-purple-500/50'
  };
  
  const textColors = {
    green: 'text-green-400',
    blue: 'text-blue-400',
    purple: 'text-purple-400'
  };

  if (!data) return null;

  const details = getDetails(data);

  return (
    <div className={`p-6 rounded-3xl bg-gradient-to-br ${colorClasses[color]} to-slate-900 border-2`}>
      {/* Header */}
      <div className="flex items-center gap-4 mb-4">
        <span className="text-4xl">{icon}</span>
        <div className="flex-1">
          <h3 className={`text-xl font-bold ${textColors[color]}`}>{name}</h3>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-sm bg-slate-800 px-3 py-1 rounded-full text-white">
              Confiance: {Math.round(data.confidence * 100)}%
            </span>
            <span className={`text-lg font-bold ${textColors[color]}`}>
              {data.predicted_home_goals} - {data.predicted_away_goals}
            </span>
          </div>
        </div>
      </div>

      {/* Explication simple */}
      <div className="mb-4 p-4 rounded-xl bg-slate-800/50">
        <p className="text-slate-300 text-sm leading-relaxed">
          <span className="font-bold text-white">💡 Comment ça marche :</span><br/>
          {shortExplanation}
        </p>
      </div>

      {/* Données */}
      <div className="grid grid-cols-2 gap-3">
        {details.map((d, i) => (
          <div key={i} className="flex justify-between items-center p-3 rounded-xl bg-slate-800/30">
            <span className="text-xs text-slate-500">{d.label}</span>
            <span className={`font-bold ${textColors[color]}`}>{d.value}</span>
          </div>
        ))}
      </div>

      {/* Analyse */}
      {data.analysis && (
        <div className="mt-4 p-3 rounded-xl bg-slate-800/30">
          <p className="text-xs text-slate-400 italic">{data.analysis}</p>
        </div>
      )}
    </div>
  );
}
