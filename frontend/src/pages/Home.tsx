/**
 * Home Page - Design Premium Responsive
 */
import { useState, useEffect } from 'react';
import MatchCard from '../components/matches/MatchCard';
import { getMatches, getCompetitions } from '../lib/api';
import type { Match, Competition } from '../types';

const COMPETITION_EMOJIS: Record<string, string> = {
  PL: '🏴��󠁢󠁥󠁮󠁧󠁿',
  FL1: '🇫🇷',
  BL1: '🇩🇪',
  SA: '🇮🇹',
  PD: '🇪🇸',
  CL: '🏆',
  EC: '🇪🇺',
};

export default function Home() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [competitions, setCompetitions] = useState<Competition[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCompetition, setSelectedCompetition] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const params = selectedCompetition 
          ? { competition: selectedCompetition, limit: 20 }
          : { limit: 20 };
        const [matchesData, competitionsData] = await Promise.all([
          getMatches(params),
          getCompetitions(),
        ]);
        setMatches(matchesData.matches);
        setCompetitions(competitionsData.competitions);
      } catch (err) {
        setError('Erreur de connexion au serveur');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [selectedCompetition]);

  return (
    <div className="min-h-screen">
      {/* Hero Section avec animation */}
      <div className="relative overflow-hidden py-12 md:py-20">
        {/* Background Effects */}
        <div className="absolute inset-0 bg-gradient-to-b from-blue-600/10 via-purple-600/5 to-transparent" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-gradient-to-r from-blue-500/20 via-purple-500/20 to-pink-500/20 blur-3xl opacity-50" />
        
        <div className="relative container mx-auto px-4">
          <div className="text-center">
            {/* Animated Title */}
            <h1 className="text-4xl sm:text-5xl md:text-7xl font-black mb-6 animate-fade-in">
              <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                Prédictions
              </span>
              <br className="md:hidden" />
              <span className="text-white"> de Football</span>
            </h1>
            
            {/* Subtitle */}
            <p className="text-slate-400 text-lg md:text-xl max-w-2xl mx-auto mb-8 animate-fade-in" style={{ animationDelay: '0.1s' }}>
              Analyse basée sur <span className="text-blue-400 font-semibold">3 logiques familiales</span>
            </p>
            
            {/* Logic Pills */}
            <div className="flex flex-wrap justify-center gap-3 md:gap-6 mb-10 animate-fade-in" style={{ animationDelay: '0.2s' }}>
              <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-green-500/10 border border-green-500/30">
                <span className="w-3 h-3 rounded-full bg-green-500" />
                <span className="text-sm text-green-400 font-medium">Papa (35%)</span>
              </div>
              <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/30">
                <span className="w-3 h-3 rounded-full bg-blue-500" />
                <span className="text-sm text-blue-400 font-medium">Grand Frère (35%)</span>
              </div>
              <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-purple-500/10 border border-purple-500/30">
                <span className="w-3 h-3 rounded-full bg-purple-500" />
                <span className="text-sm text-purple-400 font-medium">Ma Logique (30%)</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Competitions Filter */}
      <div className="container mx-auto px-4 mb-8">
        <div className="flex flex-wrap justify-center gap-2 md:gap-3">
          <button
            onClick={() => setSelectedCompetition(null)}
            className={`px-4 md:px-6 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 ${
              !selectedCompetition
                ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg shadow-blue-500/30 scale-105'
                : 'bg-slate-800/80 text-slate-400 hover:bg-slate-700 hover:text-white'
            }`}
          >
            ⚽ Tous
          </button>
          {competitions.slice(0, 6).map((comp, index) => (
            <button
              key={comp.id}
              onClick={() => setSelectedCompetition(comp.code)}
              className={`px-4 md:px-5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 ${
                selectedCompetition === comp.code
                  ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg shadow-blue-500/30 scale-105'
                  : 'bg-slate-800/80 text-slate-400 hover:bg-slate-700 hover:text-white'
              }`}
              style={{ animationDelay: `${index * 0.05}s` }}
            >
              {COMPETITION_EMOJIS[comp.code] || '⚽'} {comp.code}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-4 pb-16">
        {/* Loading */}
        {loading && (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="animate-pulse bg-slate-800/50 rounded-2xl h-48 border border-slate-700/50" />
            ))}
          </div>
        )}

        {/* Error */}
        {error && !loading && (
          <div className="text-center py-20">
            <div className="inline-block p-8 rounded-3xl bg-slate-800/50 border border-red-500/30">
              <span className="text-6xl mb-6 block">⚠️</span>
              <p className="text-red-400 text-lg font-medium mb-4">{error}</p>
              <button 
                onClick={() => window.location.reload()}
                className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl text-white font-semibold hover:shadow-lg hover:shadow-blue-500/30 transition-all"
              >
                Réessayer
              </button>
            </div>
          </div>
        )}

        {/* Matches Grid */}
        {!loading && !error && (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
            {matches.map((match, index) => (
              <div 
                key={match.id} 
                className="animate-fade-in"
                style={{ animationDelay: `${index * 0.05}s` }}
              >
                <MatchCard match={match} />
              </div>
            ))}
          </div>
        )}

        {/* Empty */}
        {!loading && !error && matches.length === 0 && (
          <div className="text-center py-20">
            <div className="inline-block p-8 rounded-3xl bg-slate-800/50 border border-slate-700/50">
              <span className="text-6xl mb-6 block">📭</span>
              <p className="text-slate-400 text-lg">Aucun match disponible</p>
              <p className="text-slate-500 text-sm mt-2">
                Essaie une autre compétition
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
