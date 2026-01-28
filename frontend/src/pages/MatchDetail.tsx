/**
 * MatchDetail Page - Affiche la prédiction stockée en BD avec les 3 logiques
 */
import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getMatch, getApex30Report } from '../lib/api';
import type { Match, Apex30FullReport } from '../types';

export default function MatchDetail() {
  const { id } = useParams<{ id: string }>();
  const [match, setMatch] = useState<Match | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [apexReport, setApexReport] = useState<Apex30FullReport | null>(null);
  const [showFullLogic, setShowFullLogic] = useState(false);
  const [loadingReport, setLoadingReport] = useState(false);

  const parseImportantMatch = (jsonStr?: string) => {
    if (!jsonStr) return null;
    try {
      return JSON.parse(jsonStr);
    } catch {
      return null;
    }
  };


  useEffect(() => {
    async function fetchData() {
      if (!id) return;
      try {
        setLoading(true);
        const matchData = await getMatch(parseInt(id));
        setMatch(matchData);
      } catch (err) {
        setError('Match non trouvé');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [id]);

  const fetchFullAnalysis = async () => {
    if (!id || apexReport) {
      setShowFullLogic(true);
      return;
    }
    
    try {
      setLoadingReport(true);
      const report = await getApex30Report(parseInt(id));
      setApexReport(report);
      setShowFullLogic(true);
    } catch (err) {
      console.error("Erreur lors de la récupération du rapport APEX-30", err);
      // Fallback: montrer quand même la modal avec un message d'erreur ou données partielles
      setShowFullLogic(true);
    } finally {
      setLoadingReport(false);
    }
  };

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
  const prediction = match.prediction;

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
            {/* Final Prediction Banner - CONSENSUS */}
            <div className="mb-10 p-6 md:p-8 rounded-3xl bg-gradient-to-r from-blue-900/50 via-purple-900/50 to-pink-900/50 border border-blue-500/30">
              <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                <div className="flex items-center gap-4">
                  <span className="text-4xl">🎯</span>
                  <div>
                    <h3 className="text-xl font-bold text-white">Prédiction Finale (Consensus)</h3>
                    <p className="text-slate-400 text-sm">Moyenne pondérée des 3 logiques familiales</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-8">
                  <div className="text-center">
                    <div className="flex items-center gap-3 px-6 py-3 rounded-xl bg-slate-900/50 border border-slate-700">
                      <span className="text-4xl font-black text-white">{prediction.home_score_forecast}</span>
                      <span className="text-2xl text-slate-500">-</span>
                      <span className="text-4xl font-black text-white">{prediction.away_score_forecast}</span>
                    </div>
                  </div>
                  
                  <div className="text-center">
                    <span className="inline-block px-5 py-2.5 rounded-xl font-bold text-lg bg-blue-500/20 text-blue-400 border border-blue-500/50">
                      {prediction.bet_tip || 'N/A'}
                    </span>
                    <p className="text-xs text-slate-500 mt-2">
                      Confiance: {Math.round((prediction.confidence || 0) * 100)}%
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Three Logic Cards */}
            <div className="grid md:grid-cols-3 gap-6 mb-10">
              {/* Papa Logic */}
              <div className="rounded-2xl bg-gradient-to-br from-green-600/20 to-emerald-600/20 border border-green-500/50 p-5">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">🟢</span>
                    <div>
                      <span className="font-bold text-lg text-green-400">Papa</span>
                      <span className="text-xs text-slate-500 ml-2">(Le Classement)</span>
                    </div>
                  </div>
                  <span className="text-sm text-slate-400">{Math.round((prediction.papa_confidence || 0) * 100)}%</span>
                </div>

                <p className="text-xs text-slate-400 mb-4 italic">
                  📊 Regarde qui est mieux classé au championnat. Le 1er bat souvent le dernier !
                </p>

                <div className="text-center mb-4">
                  <div className="inline-flex items-center gap-3 px-6 py-3 rounded-xl bg-slate-900/50">
                    <span className="text-3xl font-black text-white">{prediction.papa_home_score || 0}</span>
                    <span className="text-xl text-slate-500">-</span>
                    <span className="text-3xl font-black text-white">{prediction.papa_away_score || 0}</span>
                  </div>
                </div>

                <div className="text-center mb-4">
                  <span className="inline-block px-4 py-1.5 rounded-full text-sm font-bold bg-gradient-to-r from-green-600/20 to-emerald-600/20 text-green-400 border border-green-500/50">
                    {prediction.papa_tip || 'N/A'}
                  </span>
                </div>

                {/* CALCUL DÉTAILLÉ - Comment Papa a obtenu ce résultat */}
                {match.home_standing_position && match.away_standing_position && (
                  <div className="bg-slate-900/50 border border-green-500/30 rounded-lg p-3 mb-4 mt-4">
                    <p className="text-xs text-green-300 font-bold mb-3 flex items-center gap-2">
                      🧮 CALCUL PAPA - Étape par étape :
                    </p>
                    
                    <div className="space-y-3 text-xs">
                      {/* Étape 1 : Force brute basée sur position */}
                      <div className="bg-slate-800/50 rounded p-2">
                        <p className="text-green-400 font-semibold mb-1">1️⃣ Force basée sur la position :</p>
                        <div className="text-slate-300 space-y-1 pl-3">
                          <p>
                            • {match.home_team} : Position #{match.home_standing_position} 
                            → Force = 1 - ({match.home_standing_position}/20) 
                            = <strong className="text-white">
                              {(1 - match.home_standing_position / 20).toFixed(2)}
                            </strong> (={((1 - match.home_standing_position / 20) * 100).toFixed(0)}%)
                          </p>
                          <p>
                            • {match.away_team} : Position #{match.away_standing_position} 
                            → Force = 1 - ({match.away_standing_position}/20) 
                            = <strong className="text-white">
                              {(1 - match.away_standing_position / 20).toFixed(2)}
                            </strong> (={((1 - match.away_standing_position / 20) * 100).toFixed(0)}%)
                          </p>
                        </div>
                      </div>

                      {/* Étape 2 : Ajustement niveau ligue */}
                      <div className="bg-slate-800/50 rounded p-2">
                        <p className="text-green-400 font-semibold mb-1">2️⃣ Ajustement niveau ligue :</p>
                        <div className="text-slate-300 space-y-1 pl-3">
                          <p>
                            • Niveau {match.competition_name} = <strong className="text-white">85%</strong> (estimation)
                          </p>
                          <p>
                            • Force ajustée {match.home_team} = {(1 - match.home_standing_position / 20).toFixed(2)} × 0.85 
                            = <strong className="text-green-400">
                              {((1 - match.home_standing_position / 20) * 0.85).toFixed(2)}
                            </strong>
                          </p>
                          <p>
                            • Force ajustée {match.away_team} = {(1 - match.away_standing_position / 20).toFixed(2)} × 0.85 
                            = <strong className="text-blue-400">
                              {((1 - match.away_standing_position / 20) * 0.85).toFixed(2)}
                            </strong>
                          </p>
                        </div>
                      </div>

                      {/* Étape 3 : Différence et prédiction */}
                      <div className="bg-slate-800/50 rounded p-2">
                        <p className="text-green-400 font-semibold mb-1">3️⃣ Prédiction finale :</p>
                        <div className="text-slate-300 space-y-1 pl-3">
                          <p>
                            • Écart = {((1 - match.home_standing_position / 20) * 0.85).toFixed(2)} 
                            - {((1 - match.away_standing_position / 20) * 0.85).toFixed(2)} 
                            = <strong className="text-white">
                              {(((1 - match.home_standing_position / 20) - (1 - match.away_standing_position / 20)) * 0.85).toFixed(2)}
                            </strong>
                          </p>
                          <p>
                            • {Math.abs(((1 - match.home_standing_position / 20) - (1 - match.away_standing_position / 20)) * 0.85) > 0.15 
                              ? (((1 - match.home_standing_position / 20) - (1 - match.away_standing_position / 20)) * 0.85) > 0 
                                ? "✅ Écart significatif → Domicile favori" 
                                : "✅ Écart significatif → Extérieur favori"
                              : "⚖️ Écart faible → Match équilibré"}
                          </p>
                          <p className="text-green-300 font-bold mt-2">
                            → Résultat Papa : {prediction.papa_home_score} - {prediction.papa_away_score}
                          </p>
                        </div>
                      </div>

                      {/* Note explicative */}
                      <div className="border-t border-slate-700 pt-2">
                        <p className="text-slate-400 italic text-[10px] leading-relaxed">
                          💡 <strong>Note :</strong> Papa multiplie la force par la moyenne de buts de chaque équipe, 
                          puis ajuste selon l'écart (+20% pour le favori, -20% pour le moins fort). Les scores sont 
                          arrondis et limités entre 0 et 5 buts.
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* PREUVES Papa - EXPLICATIONS COMPLÈTES */}
                <div className="border-t border-green-500/20 pt-4 mt-4">
                  <p className="text-xs text-green-400 uppercase tracking-wide mb-3 flex items-center gap-2 font-bold">
                    <span>📊</span> PREUVES - POURQUOI CE RÉSULTAT ?
                  </p>
                  
                  {/* Explication du contexte */}
                  <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-3 mb-4">
                    <p className="text-xs text-green-300 font-semibold mb-2">🎯 Ce que Papa regarde :</p>
                    <p className="text-xs text-slate-300 leading-relaxed">
                      Papa analyse le <strong>classement actuel</strong> du championnat. Une équipe bien classée 
                      (top 3) a statistiquement plus de chances de gagner qu'une équipe mal classée (bottom 5). 
                      Papa compare aussi le <strong>niveau du championnat</strong> : la Ligue 1 (85%) est plus 
                      relevée que la ligue norvégienne (52%), donc une 5ème place en Ligue 1 peut battre un 
                      1er de Norvège !
                    </p>
                  </div>

                  <div className="space-y-3 text-xs">
                    {/* Position et points avec explications */}
                    <div className="bg-slate-800/50 rounded-lg p-3">
                      <p className="text-green-400 font-bold mb-2">📍 Positions actuelles au classement :</p>
                      
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-slate-300">{match.home_team}</span>
                        <span className="text-white font-bold bg-slate-700/50 px-3 py-1 rounded">
                          {match.home_standing_position ? `#${match.home_standing_position}` : 'Position inconnue'}
                          {match.home_standing_points ? ` • ${match.home_standing_points} pts` : ''}
                        </span>
                      </div>
                      
                      <div className="flex justify-between items-center">
                        <span className="text-slate-300">{match.away_team}</span>
                        <span className="text-white font-bold bg-slate-700/50 px-3 py-1 rounded">
                          {match.away_standing_position ? `#${match.away_standing_position}` : 'Position inconnue'}
                          {match.away_standing_points ? ` • ${match.away_standing_points} pts` : ''}
                        </span>
                      </div>

                      {/* Explication de la différence */}
                      {match.home_standing_position && match.away_standing_position && (
                        <div className="mt-3 pt-3 border-t border-slate-600/50">
                          <p className="text-xs text-slate-400 italic">
                            💡 <strong>Écart au classement :</strong> 
                            {Math.abs(match.home_standing_position - match.away_standing_position)} places de différence.
                            {Math.abs(match.home_standing_position - match.away_standing_position) > 5 
                              ? " C'est significatif ! L'équipe mieux classée a un avantage clair." 
                              : " C'est serré ! Les deux équipes sont au même niveau au classement."}
                          </p>
                        </div>
                      )}
                    </div>
                    
                    {/* Niveau de ligue avec explication */}
                    <div className="bg-slate-800/50 rounded-lg p-3">
                      <p className="text-green-400 font-bold mb-2">🏆 Niveau du championnat :</p>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-slate-300">Compétition</span>
                        <span className="text-green-400 font-bold">{match.competition_name}</span>
                      </div>
                      <p className="text-xs text-slate-400 italic mt-2">
                        💡 <strong>Importance :</strong> Les championnats de top niveau (Premier League, La Liga, 
                        Ligue 1, Champions League) ont des équipes plus fortes. Papa en tient compte quand il 
                        compare des équipes de championnats différents. Par exemple, un 10ème de Premier League 
                        peut battre un 3ème de Championship.
                      </p>
                    </div>

                    {/* Matchs importants à venir */}
                    <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-3">
                      <p className="text-yellow-400 font-bold mb-2">🔜 Match important à venir (3 jours) :</p>
                      
                      {(() => {
                        const homeUp = parseImportantMatch(prediction.home_upcoming_important);
                        const awayUp = parseImportantMatch(prediction.away_upcoming_important);
                        
                        if (!homeUp && !awayUp) {
                          return (
                            <p className="text-xs text-slate-400 italic">
                              Aucun match de coupe ou de ligue des champions détecté pour les deux équipes dans les 3 prochains jours.
                            </p>
                          );
                        }

                        return (
                          <div className="space-y-2">
                            {homeUp && (
                              <div className="text-xs p-2 bg-yellow-500/10 rounded border border-yellow-500/20">
                                <span className="text-white font-bold">{match.home_team}</span> joue en <span className="text-yellow-300">{homeUp.competition}</span> contre <span className="font-semibold text-white">{homeUp.opponent}</span> dans <span className="text-yellow-300">{homeUp.days_until} jours</span>.
                              </div>
                            )}
                            {awayUp && (
                              <div className="text-xs p-2 bg-yellow-500/10 rounded border border-yellow-500/20">
                                <span className="text-white font-bold">{match.away_team}</span> joue en <span className="text-yellow-300">{awayUp.competition}</span> contre <span className="font-semibold text-white">{awayUp.opponent}</span> dans <span className="text-yellow-300">{awayUp.days_until} jours</span>.
                              </div>
                            )}
                            <p className="text-[10px] text-slate-400 italic mt-2">
                              💡 Papa a réduit la confiance car le coach pourrait faire tourner l'effectif.
                            </p>
                          </div>
                        );
                      })()}
                    </div>
                    
                    {/* Matchs importants récents */}
                    <div className="bg-orange-900/20 border border-orange-500/30 rounded-lg p-3">
                      <p className="text-orange-400 font-bold mb-2">⏮️ Match important récent (3 jours) :</p>
                      
                      {(() => {
                        const homeRec = parseImportantMatch(prediction.home_recent_important);
                        const awayRec = parseImportantMatch(prediction.away_recent_important);
                        
                        if (!homeRec && !awayRec) {
                          return (
                            <p className="text-xs text-slate-400 italic">
                              Aucun match intense récent détecté pour les deux équipes dans les 3 derniers jours.
                            </p>
                          );
                        }

                        return (
                          <div className="space-y-2">
                            {homeRec && (
                              <div className="text-xs p-2 bg-orange-500/10 rounded border border-orange-500/20">
                                <span className="text-white font-bold">{match.home_team}</span> a joué en <span className="text-orange-300">{homeRec.competition}</span> il y a <span className="text-orange-300">{homeRec.days_ago} jours</span> (Score: {homeRec.score}).
                              </div>
                            )}
                            {awayRec && (
                              <div className="text-xs p-2 bg-orange-500/10 rounded border border-orange-500/20">
                                <span className="text-white font-bold">{match.away_team}</span> a joué en <span className="text-orange-300">{awayRec.competition}</span> il y a <span className="text-orange-300">{awayRec.days_ago} jours</span> (Score: {awayRec.score}).
                              </div>
                            )}
                            <p className="text-[10px] text-slate-400 italic mt-2">
                              💡 Papa a pris en compte la fatigue physique possible des joueurs.
                            </p>
                          </div>
                        );
                      })()}
                    </div>

                    {/* Résumé final */}
                    <div className="bg-green-900/30 border border-green-500/50 rounded-lg p-3 mt-4">
                      <p className="text-green-300 font-bold mb-2">✅ EN RÉSUMÉ - Logique Papa :</p>
                      <ul className="space-y-1 text-xs text-slate-300">
                        <li>• Équipe mieux classée = Plus de chances de gagner</li>
                        <li>• Gros écart de points = Avantage significatif</li>
                        <li>• Championnat relevé = Équipes plus fortes</li>
                        <li>• Match important proche = Risque de rotation/fatigue</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              {/* Grand Frère Logic */}
              <div className="rounded-2xl bg-gradient-to-br from-blue-600/20 to-cyan-600/20 border border-blue-500/50 p-5">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">�</span>
                    <div>
                      <span className="font-bold text-lg text-blue-400">Grand Frère</span>
                      <span className="text-xs text-slate-500 ml-2">(Historique & Domicile)</span>
                    </div>
                  </div>
                  <span className="text-sm text-slate-400">{Math.round((prediction.grand_frere_confidence || 0) * 100)}%</span>
                </div>

                <p className="text-xs text-slate-400 mb-4 italic">
                  🏠 Regarde qui gagne quand ces 2 équipes se rencontrent, et si jouer à la maison aide !
                </p>

                <div className="text-center mb-4">
                  <div className="inline-flex items-center gap-3 px-6 py-3 rounded-xl bg-slate-900/50">
                    <span className="text-3xl font-black text-white">{prediction.grand_frere_home_score || 0}</span>
                    <span className="text-xl text-slate-500">-</span>
                    <span className="text-3xl font-black text-white">{prediction.grand_frere_away_score || 0}</span>
                  </div>
                </div>

                <div className="text-center mb-4">
                  <span className="inline-block px-4 py-1.5 rounded-full text-sm font-bold bg-gradient-to-r from-blue-600/20 to-cyan-600/20 text-blue-400 border border-blue-500/50">
                    {prediction.grand_frere_tip || 'N/A'}
                  </span>
                </div>

                <p className="text-xs text-slate-400 italic mb-4">
                  "{prediction.grand_frere_tip ? `Grand Frère dit : ${prediction.grand_frere_tip}` : 'Pas de conseil Grand Frère'}"
                </p>

                {/* CALCUL DÉTAILLÉ - Comment Grand Frère a obtenu ce résultat */}
                {(prediction.h2h_home_wins !== undefined || prediction.h2h_matches_count) && (
                  <div className="bg-slate-900/50 border border-blue-500/30 rounded-lg p-3 mb-4 mt-4">
                    <p className="text-xs text-blue-300 font-bold mb-3 flex items-center gap-2">
                      🧮 CALCUL GRAND FRÈRE - Étape par étape :
                    </p>
                    
                    <div className="space-y-3 text-xs">
                      {/* Étape 1 : Force H2H */}
                      <div className="bg-slate-800/50 rounded p-2">
                        <p className="text-blue-400 font-semibold mb-1">1️⃣ Score H2H basé sur les confrontations :</p>
                        <div className="text-slate-300 space-y-1 pl-3">
                          <p>
                            • {match.home_team} : {prediction.h2h_home_wins || 0} victoires × 3 + {prediction.h2h_draws || 0} nuls × 1 
                            = <strong className="text-white">
                              {((prediction.h2h_home_wins || 0) * 3 + (prediction.h2h_draws || 0) * 1)} pts
                            </strong>
                          </p>
                          <p>
                            • {match.away_team} : {prediction.h2h_away_wins || 0} victoires × 3 + {prediction.h2h_draws || 0} nuls × 1 
                            = <strong className="text-white">
                              {((prediction.h2h_away_wins || 0) * 3 + (prediction.h2h_draws || 0) * 1)} pts
                            </strong>
                          </p>
                          <p className="text-slate-400 italic text-[10px]">
                            (Victoire = 3 pts, Nul = 1 pt pour les deux)
                          </p>
                        </div>
                      </div>

                      {/* Étape 2 : Score H2H normalisé */}
                      <div className="bg-slate-800/50 rounded p-2">
                        <p className="text-blue-400 font-semibold mb-1">2️⃣ Force H2H normalisée (0 à 1) :</p>
                        <div className="text-slate-300 space-y-1 pl-3">
                          {(() => {
                            const totalMatches = (prediction.h2h_home_wins || 0) + (prediction.h2h_away_wins || 0) + (prediction.h2h_draws || 0);
                            const homeScore = ((prediction.h2h_home_wins || 0) * 3 + (prediction.h2h_draws || 0) * 1) / (totalMatches * 3 || 1);
                            const awayScore = ((prediction.h2h_away_wins || 0) * 3 + (prediction.h2h_draws || 0) * 1) / (totalMatches * 3 || 1);
                            return (
                              <>
                                <p>
                                  • {match.home_team} : Force H2H = <strong className="text-green-400">{homeScore.toFixed(2)}</strong> ({(homeScore * 100).toFixed(0)}%)
                                </p>
                                <p>
                                  • {match.away_team} : Force H2H = <strong className="text-blue-400">{awayScore.toFixed(2)}</strong> ({(awayScore * 100).toFixed(0)}%)
                                </p>
                              </>
                            );
                          })()}
                        </div>
                      </div>

                      {/* Étape 3 : Bonus domicile */}
                      <div className="bg-slate-800/50 rounded p-2">
                        <p className="text-blue-400 font-semibold mb-1">3️⃣ Ajout du bonus domicile :</p>
                        <div className="text-slate-300 space-y-1 pl-3">
                          <p>
                            • Bonus domicile = <strong className="text-green-400">+{Math.round((prediction.gf_home_advantage_bonus || 0.1) * 100)}%</strong>
                          </p>
                          <p>
                            • Force finale {match.home_team} = Force H2H + Bonus = 
                            <strong className="text-green-400 ml-1">
                              {(() => {
                                const totalMatches = (prediction.h2h_home_wins || 0) + (prediction.h2h_away_wins || 0) + (prediction.h2h_draws || 0);
                                const homeScore = ((prediction.h2h_home_wins || 0) * 3 + (prediction.h2h_draws || 0) * 1) / (totalMatches * 3 || 1);
                                return (homeScore + (prediction.gf_home_advantage_bonus || 0.1)).toFixed(2);
                              })()}
                            </strong>
                          </p>
                        </div>
                      </div>

                      {/* Étape 4 : Prédiction finale */}
                      <div className="bg-slate-800/50 rounded p-2">
                        <p className="text-blue-400 font-semibold mb-1">4️⃣ Prédiction finale :</p>
                        <div className="text-slate-300 space-y-1 pl-3">
                          <p>
                            • Score basé sur la force × moyenne de buts de chaque équipe
                          </p>
                          <p className="text-blue-300 font-bold mt-2">
                            → Résultat Grand Frère : {prediction.grand_frere_home_score} - {prediction.grand_frere_away_score}
                          </p>
                        </div>
                      </div>

                      {/* Note explicative */}
                      <div className="border-t border-slate-700 pt-2">
                        <p className="text-slate-400 italic text-[10px] leading-relaxed">
                          💡 <strong>Note :</strong> Grand Frère utilise l'historique des confrontations directes (H2H) 
                          et ajoute un bonus domicile. Celui qui gagne souvent les H2H a l'ascendant psychologique. 
                          Le bonus domicile est ajusté selon l'écart de force entre les équipes.
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* PREUVES Grand Frère */}
                <div className="border-t border-blue-500/20 pt-4 mt-4">
                  <p className="text-xs text-blue-400 uppercase tracking-wide mb-3 flex items-center gap-2 font-bold">
                    <span>🏠</span> PREUVES - HISTORIQUE & DOMICILE
                  </p>
                  
                  <div className="space-y-3 text-xs">
                    {/* H2H Stats */}
                    <div className="bg-slate-800/50 rounded-lg p-3">
                      <p className="text-blue-400 font-bold mb-2">⚔️ Face-à-Face (H2H) - {prediction.h2h_matches_count || 0} dernières confrontations :</p>
                      <div className="grid grid-cols-3 gap-2 text-center">
                        <div className="bg-slate-700/50 p-2 rounded">
                          <p className="text-green-400 font-bold text-lg">{prediction.h2h_home_wins || 0}</p>
                          <p className="text-[10px] text-slate-400 uppercase">Gagnés {match.home_team}</p>
                        </div>
                        <div className="bg-slate-700/50 p-2 rounded">
                          <p className="text-yellow-400 font-bold text-lg">{prediction.h2h_draws || 0}</p>
                          <p className="text-[10px] text-slate-400 uppercase">Nuls</p>
                        </div>
                        <div className="bg-slate-700/50 p-2 rounded">
                          <p className="text-red-400 font-bold text-lg">{prediction.h2h_away_wins || 0}</p>
                          <p className="text-[10px] text-slate-400 uppercase">Gagnés {match.away_team}</p>
                        </div>
                      </div>
                      <p className="text-[10px] text-slate-400 italic mt-2">
                        💡 Grand Frère regarde les 10 dernières confrontations pour voir qui a l'ascendant psychologique.
                      </p>
                    </div>

                    {/* H2H Goals Analysis */}
                    <div className="bg-slate-800/50 rounded-lg p-3">
                      <p className="text-blue-400 font-bold mb-2">⚽ Buts marqués dans les H2H :</p>
                      <div className="grid grid-cols-2 gap-3">
                        <div className="bg-slate-700/50 p-2 rounded text-center">
                          <p className="text-white font-bold text-xl">{prediction.h2h_home_goals_total || 0}</p>
                          <p className="text-[10px] text-slate-400">Total {match.home_team}</p>
                          <p className="text-blue-300 font-semibold">{prediction.h2h_home_goals_freq || 0} but/match</p>
                        </div>
                        <div className="bg-slate-700/50 p-2 rounded text-center">
                          <p className="text-white font-bold text-xl">{prediction.h2h_away_goals_total || 0}</p>
                          <p className="text-[10px] text-slate-400">Total {match.away_team}</p>
                          <p className="text-blue-300 font-semibold">{prediction.h2h_away_goals_freq || 0} but/match</p>
                        </div>
                      </div>
                      <div className="mt-2 p-2 bg-blue-500/10 border border-blue-500/20 rounded">
                        <p className="text-[10px] text-white">
                          📊 <strong>Total :</strong> {(prediction.h2h_home_goals_total || 0) + (prediction.h2h_away_goals_total || 0)} buts en {prediction.h2h_matches_count || 0} matchs
                          {prediction.h2h_top_scorer === "home" && <span className="text-green-400 ml-2">→ {match.home_team} marque plus !</span>}
                          {prediction.h2h_top_scorer === "away" && <span className="text-red-400 ml-2">→ {match.away_team} marque plus !</span>}
                          {prediction.h2h_top_scorer === "equal" && <span className="text-yellow-400 ml-2">→ Égalité parfaite !</span>}
                        </p>
                      </div>
                    </div>

                    {/* Home Advantage */}
                    <div className="bg-slate-800/50 rounded-lg p-3">
                      <p className="text-blue-400 font-bold mb-2">🏡 Avantage Domicile :</p>
                      <div className="flex justify-between items-center bg-blue-500/10 border border-blue-500/20 p-2 rounded text-white">
                        <span>Bonus calculé</span>
                        <span className="font-bold text-green-400">+{Math.round((prediction.gf_home_advantage_bonus || 0.1) * 100)}% pour {match.home_team}</span>
                      </div>
                      <p className="text-[10px] text-slate-400 italic mt-2">
                        💡 L'avantage domicile est ajusté selon l'écart de force entre les équipes.
                      </p>
                    </div>

                    {/* Verdict Grand Frère */}
                    {prediction.gf_verdict && (
                      <div className="bg-blue-900/40 border border-blue-400/50 rounded-lg p-3">
                        <p className="text-blue-300 font-bold mb-2">🎯 VERDICT GRAND FRÈRE :</p>
                        <p className="text-white text-sm leading-relaxed">{prediction.gf_verdict}</p>
                      </div>
                    )}

                    {/* Résumé Grand Frère */}
                    <div className="bg-blue-900/30 border border-blue-500/50 rounded-lg p-3">
                      <p className="text-blue-300 font-bold mb-2">✅ EN RÉSUMÉ - Grand Frère :</p>
                      <ul className="space-y-1 text-xs text-slate-300">
                        <li>• Historique favorable = Avantage confiance</li>
                        <li>• Jeu à domicile = Bonus de force (+{Math.round((prediction.gf_home_advantage_bonus || 0.1) * 100)}%)</li>
                        <li>• Qui marque le plus ? {prediction.h2h_top_scorer === "home" ? match.home_team : prediction.h2h_top_scorer === "away" ? match.away_team : "Égalité"}</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              {/* Ma Logique */}
              <div className="rounded-2xl bg-gradient-to-br from-purple-600/20 to-pink-600/20 border border-purple-500/50 p-5">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">🟣</span>
                    <div>
                      <span className="font-bold text-lg text-purple-400">Ma Logique</span>
                      <span className="text-xs text-slate-500 ml-2">(Forme Récente)</span>
                    </div>
                  </div>
                  <span className="text-sm text-slate-400">{Math.round((prediction.ma_logique_confidence || 0) * 100)}%</span>
                </div>

                <p className="text-xs text-slate-400 mb-4 italic">
                  � Regarde les 10 derniers matchs. Une équipe en forme a plus de chances de continuer !
                </p>

                <div className="text-center mb-4">
                  <div className="inline-flex items-center gap-3 px-6 py-3 rounded-xl bg-slate-900/50">
                    <span className="text-3xl font-black text-white">{prediction.ma_logique_home_score || 0}</span>
                    <span className="text-xl text-slate-500">-</span>
                    <span className="text-3xl font-black text-white">{prediction.ma_logique_away_score || 0}</span>
                  </div>
                </div>

                <div className="text-center mb-4">
                  <span className="inline-block px-4 py-1.5 rounded-full text-sm font-bold bg-gradient-to-r from-purple-600/20 to-pink-600/20 text-purple-400 border border-purple-500/50">
                    {prediction.ma_logique_tip || 'N/A'}
                  </span>
                </div>

                <p className="text-xs text-slate-400 italic mb-4">
                  "{prediction.ma_logique_tip ? `Ma Logique suggère : ${prediction.ma_logique_tip}` : 'Pas de conseil Ma Logique'}"
                </p>

                {/* Version Simplifiée Ma Logique */}
                <div className="border-t border-purple-500/20 pt-4 mt-4">
                  <p className="text-purple-400 uppercase tracking-wide mb-3 flex items-center gap-2 font-bold text-xs">
                    <span>🧠</span> ANALYSE SCIENTIFIQUE APEX-30
                  </p>
                  
                  <div className="bg-slate-900/40 rounded-xl p-4 border border-purple-500/20 mb-4">
                    <p className="text-sm text-slate-300 leading-relaxed mb-3">
                      Le moteur <strong>APEX-30</strong> a analysé ce match sur 8 modules techniques (IFP, Fatigue, Motivation, H2H...). 
                    </p>
                    <div className="flex items-center gap-2 text-xs text-purple-300 bg-purple-500/10 p-2 rounded-lg border border-purple-500/20">
                      <span>💡</span>
                      <span>L'indice de confiance est de {Math.round((prediction.ma_logique_confidence || 0) * 100)}% basé sur la convergence des indicateurs.</span>
                    </div>
                  </div>

                  <button 
                    onClick={fetchFullAnalysis}
                    disabled={loadingReport}
                    className="w-full py-3 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-sm shadow-lg shadow-purple-900/20 transition-all flex items-center justify-center gap-2 group"
                  >
                    {loadingReport ? (
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    ) : (
                      <>
                        <span>📄 Ma logique complète, cliquez ici</span>
                        <span className="group-hover:translate-x-1 transition-transform">→</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Explanation Section */}
            <div className="mt-10 p-6 rounded-2xl bg-slate-800/50 border border-slate-700/50">
              <h4 className="text-lg font-bold text-white mb-3">💡 Pourquoi on garde les 3 logiques ?</h4>
              <div className="space-y-2 text-slate-400 text-sm">
                <p><strong className="text-green-400">🟢 Papa (Classement):</strong> Fiable pour les grandes ligues. Si une équipe est 1ère, elle a plus de chances de gagner.</p>
                <p><strong className="text-blue-400">🔵 Grand Frère (Domicile & H2H):</strong> Utile quand 2 équipes se connaissent bien. L'avantage à domicile compte beaucoup !</p>
                <p><strong className="text-purple-400">🟣 Ma Logique (Forme):</strong> Parfaite pour voir qui est "chaud" en ce moment. La forme du moment &gt; le classement parfois.</p>
                <p className="pt-2 border-t border-slate-700 mt-3">
                  🎯 <strong>Le Consensus</strong> combine intelligemment les 3. Si les 3 sont d'accord → forte confiance. Si elles divergent → prudence !
                </p>
              </div>
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

      {/* MODAL - ANALYSE COMPLÈTE APEX-30 */}
      {showFullLogic && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
          {/* Overlay */}
          <div 
            className="absolute inset-0 bg-slate-950/80 backdrop-blur-md"
            onClick={() => setShowFullLogic(false)}
          />
          
          {/* Modal Content */}
          <div className="relative w-full max-w-4xl max-h-[90vh] overflow-hidden bg-slate-900 border border-slate-700 rounded-3xl shadow-2xl flex flex-col">
            {/* Header */}
            <div className="p-6 border-b border-slate-800 flex items-center justify-between bg-gradient-to-r from-slate-900 to-purple-900/20">
              <div className="flex items-center gap-3">
                <span className="text-3xl">🧠</span>
                <div>
                  <h2 className="text-xl font-black text-white leading-tight">Rapport Technique APEX-30</h2>
                  <p className="text-xs text-purple-400 font-bold uppercase tracking-widest">Analyse Approfondie des 8 Modules</p>
                </div>
              </div>
              <button 
                onClick={() => setShowFullLogic(false)}
                className="w-10 h-10 rounded-full bg-slate-800 text-slate-400 hover:text-white flex items-center justify-center transition-colors"
              >
                ✕
              </button>
            </div>

            {/* Scrollable Body */}
            <div className="flex-1 overflow-y-auto p-6 space-y-8 custom-scrollbar">
              {apexReport ? (
                <>
                  <div className="bg-purple-500/10 border border-purple-500/20 rounded-2xl p-4 flex items-start gap-4">
                    <span className="text-2xl mt-1">💡</span>
                    <div>
                      <h4 className="font-bold text-white mb-1">Résumé de l'expert</h4>
                      <p className="text-sm text-slate-300 leading-relaxed italic">
                        "{apexReport.summary}"
                      </p>
                    </div>
                  </div>

                  {/* Table header */}
                  <div className="hidden md:grid grid-cols-12 gap-4 px-4 py-2 text-[10px] font-bold text-slate-500 uppercase tracking-widest border-b border-slate-800">
                    <div className="col-span-4 text-left">Module d'analyse</div>
                    <div className="col-span-1 text-center">Poids</div>
                    <div className="col-span-3 text-center">Score {match?.home_team_short || 'Dom.'} vs {match?.away_team_short || 'Ext.'}</div>
                    <div className="col-span-4 text-left">Interprétation Tactique</div>
                  </div>

                  {/* Modules rows */}
                  <div className="space-y-4">
                    {apexReport.modules.map((mod) => (
                      <div key={mod.id} className="bg-slate-800/30 rounded-2xl border border-slate-800 p-4 md:p-0 md:bg-transparent md:border-0 md:rounded-none md:grid md:grid-cols-12 md:gap-4 md:items-center hover:bg-slate-800/20 transition-colors">
                        {/* Mobile Module Name */}
                        <div className="md:col-span-4 mb-3 md:mb-0 md:px-4">
                          <h5 className="font-bold text-white text-sm md:text-base">{mod.nom}</h5>
                          <p className="text-[10px] text-slate-500 italic mt-0.5">{mod.description}</p>
                        </div>

                        {/* Poids */}
                        <div className="hidden md:block md:col-span-1 text-center">
                          <span className="text-xs font-bold text-slate-400">{mod.poids}%</span>
                        </div>

                        {/* Scores */}
                        <div className="md:col-span-3 flex items-center justify-center gap-4 mb-4 md:mb-0">
                          <div className="text-center">
                            <span className={`inline-block w-10 h-10 rounded-xl flex items-center justify-center font-bold text-lg ${mod.home_val >= mod.away_val ? 'bg-purple-600 text-white' : 'bg-slate-800 text-slate-400'}`}>
                              {mod.home_val.toFixed(1)}
                            </span>
                          </div>
                          <span className="text-slate-600 font-bold">vs</span>
                          <div className="text-center">
                            <span className={`inline-block w-10 h-10 rounded-xl flex items-center justify-center font-bold text-lg ${mod.away_val > mod.home_val ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400'}`}>
                              {mod.away_val.toFixed(1)}
                            </span>
                          </div>
                        </div>

                        {/* Detail Analyse */}
                        <div className="md:col-span-4 md:px-4 border-t border-slate-800 pt-3 md:border-0 md:pt-0">
                          <p className="text-xs text-slate-300 leading-relaxed">
                            {mod.analyse}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <div className="py-20 text-center">
                  <div className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                  <p className="text-slate-400">Génération du rapport technique en cours...</p>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-6 border-t border-slate-800 bg-slate-900 flex justify-between items-center text-[10px] text-slate-500 uppercase tracking-widest font-bold">
              <span>Moteur de calcul : Pronoscore APEX-30 v2.1</span>
              <span>© 2026 FOOTBALL-PREDICTION</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
