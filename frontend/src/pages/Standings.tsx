/**
 * Standings Page - Classements Modernes
 */
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getStandings } from '../lib/api';
import type { Standing } from '../types';

const COMPETITIONS = [
  { code: 'PL', name: 'Premier League', flag: '🏴󠁧󠁢󠁥󠁮󠁧󠁿', color: 'from-purple-600 to-purple-800' },
  { code: 'FL1', name: 'Ligue 1', flag: '🇫🇷', color: 'from-blue-600 to-blue-800' },
  { code: 'BL1', name: 'Bundesliga', flag: '🇩🇪', color: 'from-red-600 to-red-800' },
  { code: 'SA', name: 'Serie A', flag: '🇮🇹', color: 'from-green-600 to-green-800' },
  { code: 'PD', name: 'La Liga', flag: '🇪🇸', color: 'from-orange-600 to-orange-800' },
  { code: 'CL', name: 'Champions League', flag: '🏆', color: 'from-blue-500 to-indigo-700' },
];

function getPositionZone(position: number, total: number) {
  if (position <= 4) return { zone: 'cl', color: 'bg-blue-500', label: 'Champions League' };
  if (position <= 6) return { zone: 'uel', color: 'bg-orange-500', label: 'Europa League' };
  if (position >= total - 2) return { zone: 'relegation', color: 'bg-red-500', label: 'Relégation' };
  return { zone: 'mid', color: 'bg-transparent', label: '' };
}

export default function Standings() {
  const { competition: compParam = 'PL' } = useParams<{ competition?: string }>();
  const [standings, setStandings] = useState<Standing[]>([]);
  const [competitionName, setCompetitionName] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [competition, setCompetition] = useState(compParam);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const data = await getStandings(competition);
        setStandings(data.standings);
        setCompetitionName(data.competition_name);
      } catch (err) {
        setError('Erreur lors du chargement du classement');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [competition]);

  const currentComp = COMPETITIONS.find(c => c.code === competition) || COMPETITIONS[0];

  return (
    <div className="min-h-screen pb-16">
      {/* Hero Header */}
      <div className="relative py-12 mb-8">
        <div className={`absolute inset-0 bg-gradient-to-r ${currentComp.color} opacity-20`} />
        <div className="relative container mx-auto px-4 text-center">
          <span className="text-5xl mb-4 block">{currentComp.flag}</span>
          <h1 className="text-3xl md:text-5xl font-black text-white mb-2">
            Classement {competitionName || competition}
          </h1>
          <p className="text-slate-400">Saison 2025/2026</p>
        </div>
      </div>

      <div className="container mx-auto px-4">
        {/* Competition Tabs */}
        <div className="flex flex-wrap justify-center gap-2 md:gap-3 mb-10">
          {COMPETITIONS.map((comp) => (
            <button
              key={comp.code}
              onClick={() => setCompetition(comp.code)}
              className={`px-4 md:px-6 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 ${
                competition === comp.code
                  ? `bg-gradient-to-r ${comp.color} text-white shadow-lg scale-105`
                  : 'bg-slate-800/80 text-slate-400 hover:bg-slate-700 hover:text-white'
              }`}
            >
              {comp.flag} {comp.code}
            </button>
          ))}
        </div>

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

        {/* Standings Table */}
        {!loading && !error && (
          <div className="rounded-2xl bg-slate-900/50 border border-slate-700/50 overflow-hidden">
            {/* Legend */}
            <div className="flex flex-wrap gap-4 p-4 border-b border-slate-700/50 text-xs">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded bg-blue-500" />
                <span className="text-slate-400">Champions League</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded bg-orange-500" />
                <span className="text-slate-400">Europa League</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded bg-red-500" />
                <span className="text-slate-400">Relégation</span>
              </div>
            </div>

            {/* Table */}
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="text-xs text-slate-500 uppercase border-b border-slate-700/50">
                    <th className="py-4 px-4 text-left w-12">#</th>
                    <th className="py-4 px-4 text-left">Équipe</th>
                    <th className="py-4 px-4 text-center hidden sm:table-cell">MJ</th>
                    <th className="py-4 px-4 text-center text-green-400">V</th>
                    <th className="py-4 px-4 text-center text-slate-400">N</th>
                    <th className="py-4 px-4 text-center text-red-400">D</th>
                    <th className="py-4 px-4 text-center hidden md:table-cell">BP</th>
                    <th className="py-4 px-4 text-center hidden md:table-cell">BC</th>
                    <th className="py-4 px-4 text-center hidden sm:table-cell">DB</th>
                    <th className="py-4 px-4 text-center font-bold">Pts</th>
                  </tr>
                </thead>
                <tbody>
                  {standings.map((team) => {
                    const zone = getPositionZone(team.position, standings.length);
                    return (
                      <tr 
                        key={team.team_id} 
                        className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors group"
                      >
                        {/* Position */}
                        <td className="py-4 px-4">
                          <div className="flex items-center gap-2">
                            <span className={`w-1 h-8 rounded-full ${zone.color}`} />
                            <span className="font-bold text-white">{team.position}</span>
                          </div>
                        </td>
                        
                        {/* Team */}
                        <td className="py-4 px-4">
                          <div className="flex items-center gap-3">
                            <img 
                              src={team.team_crest} 
                              alt={team.team_name} 
                              className="w-8 h-8 object-contain"
                              onError={(e) => { e.currentTarget.style.display = 'none' }}
                            />
                            <div>
                              <p className="font-semibold text-white group-hover:text-blue-400 transition-colors">
                                {team.team_short || team.team_name}
                              </p>
                            </div>
                          </div>
                        </td>
                        
                        {/* Stats */}
                        <td className="py-4 px-4 text-center text-slate-400 hidden sm:table-cell">{team.played_games}</td>
                        <td className="py-4 px-4 text-center text-green-400 font-medium">{team.won}</td>
                        <td className="py-4 px-4 text-center text-slate-400">{team.draw}</td>
                        <td className="py-4 px-4 text-center text-red-400 font-medium">{team.lost}</td>
                        <td className="py-4 px-4 text-center text-slate-400 hidden md:table-cell">{team.goals_for}</td>
                        <td className="py-4 px-4 text-center text-slate-400 hidden md:table-cell">{team.goals_against}</td>
                        <td className="py-4 px-4 text-center hidden sm:table-cell">
                          <span className={team.goal_difference > 0 ? 'text-green-400' : team.goal_difference < 0 ? 'text-red-400' : 'text-slate-400'}>
                            {team.goal_difference > 0 ? '+' : ''}{team.goal_difference}
                          </span>
                        </td>
                        
                        {/* Points */}
                        <td className="py-4 px-4 text-center">
                          <span className="inline-block px-3 py-1.5 rounded-lg bg-slate-800 font-bold text-lg text-white">
                            {team.points}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
