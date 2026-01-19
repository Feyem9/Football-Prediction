/**
 * usePrediction Hook - Récupère la prédiction combinée d'un match
 */
import { useState, useEffect } from 'react';
import { getCombinedPrediction } from '../lib/api';
import type { CombinedPrediction } from '../types';

export function usePrediction(matchId: number | null) {
  const [prediction, setPrediction] = useState<CombinedPrediction | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!matchId) {
      setLoading(false);
      return;
    }

    async function fetchPrediction() {
      try {
        setLoading(true);
        setError(null);
        const data = await getCombinedPrediction(matchId);
        setPrediction(data);
      } catch (err) {
        setError('Prédiction non disponible');
        setPrediction(null);
      } finally {
        setLoading(false);
      }
    }
    fetchPrediction();
  }, [matchId]);

  return { prediction, loading, error };
}

export default usePrediction;
