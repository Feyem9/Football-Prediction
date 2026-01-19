/**
 * useStandings Hook - Récupère le classement d'une compétition
 */
import { useState, useEffect } from 'react';
import { getStandings } from '../lib/api';
import type { Standing } from '../types';

export function useStandings(competitionCode: string) {
  const [standings, setStandings] = useState<Standing[]>([]);
  const [competitionName, setCompetitionName] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchStandings() {
      try {
        setLoading(true);
        setError(null);
        const data = await getStandings(competitionCode);
        setStandings(data.standings);
        setCompetitionName(data.competition_name);
      } catch (err) {
        setError('Erreur lors du chargement du classement');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchStandings();
  }, [competitionCode]);

  return { standings, competitionName, loading, error };
}

export default useStandings;
