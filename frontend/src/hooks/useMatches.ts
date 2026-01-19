/**
 * useMatches Hook - Récupère les matchs depuis l'API
 */
import { useState, useEffect } from 'react';
import { getMatches } from '../lib/api';
import type { Match } from '../types';

interface UseMatchesOptions {
  competition?: string;
  limit?: number;
  offset?: number;
}

export function useMatches(options: UseMatchesOptions = {}) {
  const [matches, setMatches] = useState<Match[]>([]);
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchMatches() {
      try {
        setLoading(true);
        setError(null);
        const data = await getMatches(options);
        setMatches(data.matches);
        setCount(data.count);
      } catch (err) {
        setError('Erreur lors du chargement des matchs');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchMatches();
  }, [options.competition, options.limit, options.offset]);

  return { matches, count, loading, error };
}

export default useMatches;
