/**
 * RadarChart - Visualisation des 8 modules APEX-30
 * Compare les forces des deux équipes sur un graphique radar
 */
import { Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';
import type { TooltipItem } from 'chart.js';

// Enregistrer les composants Chart.js
ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

interface ModuleData {
  id: string;
  nom: string;
  poids: number;
  home_val: number;
  away_val: number;
  description?: string;
  analyse?: string;
}

interface RadarChartProps {
  modules: ModuleData[];
  homeTeam: string;
  awayTeam: string;
}

export default function RadarChart({ modules, homeTeam, awayTeam }: RadarChartProps) {
  if (!modules || modules.length === 0) {
    return (
      <div className="bg-slate-800/50 rounded-xl p-6 text-center text-slate-400">
        <p>Données d'analyse non disponibles</p>
      </div>
    );
  }

  // Normaliser les valeurs pour le radar (0-10)
  const normalizeValue = (value: number, id: string): number => {
    // Différentes normalisations selon le type de module
    if (id === 'solidite_defensive') {
      return Math.max(0, Math.min(10, value)); // Déjà sur 0-10
    }
    if (id === 'ifp') {
      return Math.max(0, Math.min(10, value * 2)); // IFP ~0-5 -> 0-10
    }
    if (id === 'force_offensive') {
      return Math.max(0, Math.min(10, value * 3)); // ~0-3 -> 0-10
    }
    if (id === 'facteur_domicile' || id === 'fatigue') {
      return Math.max(0, Math.min(10, (value + 1) * 5)); // -1 à 1 -> 0-10
    }
    if (id === 'motivation') {
      return Math.max(0, Math.min(10, (value + 2) * 2)); // -2 à 3 -> 0-10
    }
    if (id === 'h2h') {
      return Math.max(0, Math.min(10, value * 10)); // 0-1 -> 0-10
    }
    if (id === 'absences') {
      return Math.max(0, Math.min(10, (value + 1.5) * 4)); // -1.5 à 0 -> 0-6
    }
    return Math.max(0, Math.min(10, value * 5)); // Par défaut
  };

  const labels = modules.map(m => m.nom.split(' ')[0]); // Juste le premier mot
  const homeData = modules.map(m => normalizeValue(m.home_val, m.id));
  const awayData = modules.map(m => normalizeValue(m.away_val, m.id));

  const data = {
    labels,
    datasets: [
      {
        label: homeTeam,
        data: homeData,
        backgroundColor: 'rgba(34, 197, 94, 0.2)', // Vert
        borderColor: 'rgba(34, 197, 94, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(34, 197, 94, 1)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(34, 197, 94, 1)',
      },
      {
        label: awayTeam,
        data: awayData,
        backgroundColor: 'rgba(239, 68, 68, 0.2)', // Rouge
        borderColor: 'rgba(239, 68, 68, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(239, 68, 68, 1)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(239, 68, 68, 1)',
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: '#cbd5e1', // slate-300
          font: {
            size: 12,
            weight: 'bold' as const,
          },
          padding: 15,
        },
      },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.9)', // slate-900
        titleColor: '#f1f5f9',
        bodyColor: '#cbd5e1',
        borderColor: '#475569',
        borderWidth: 1,
        padding: 12,
        displayColors: true,
        callbacks: {
          label: function(context: TooltipItem<'radar'>) {
            const label = context.dataset.label || '';
            const value = context.raw as number;
            return `${label}: ${value.toFixed(1)}/10`;
          },
        },
      },
    },
    scales: {
      r: {
        min: 0,
        max: 10,
        beginAtZero: true,
        angleLines: {
          color: 'rgba(100, 116, 139, 0.3)', // slate-500
        },
        grid: {
          color: 'rgba(100, 116, 139, 0.2)',
        },
        pointLabels: {
          color: '#94a3b8', // slate-400
          font: {
            size: 11,
            weight: 'bold' as const,
          },
        },
        ticks: {
          color: '#64748b', // slate-500
          backdropColor: 'transparent',
          stepSize: 2,
        },
      },
    },
  };

  return (
    <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 rounded-2xl p-6 border border-slate-700/50 shadow-xl">
      <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <span className="text-2xl">📊</span>
        Comparaison APEX-30
      </h3>
      
      <div className="relative" style={{ height: '350px' }}>
        <Radar data={data} options={options} />
      </div>
      
      {/* Légende des modules */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-3">
        {modules.slice(0, 8).map((mod) => (
          <div 
            key={mod.id}
            className="bg-slate-700/30 rounded-lg p-2 text-center hover:bg-slate-600/40 transition-colors"
          >
            <div className="text-xs font-medium text-slate-400">{mod.nom.split(' ')[0]}</div>
            <div className="flex justify-center gap-2 mt-1">
              <span className="text-green-400 font-bold text-sm">
                {normalizeValue(mod.home_val, mod.id).toFixed(1)}
              </span>
              <span className="text-slate-500">vs</span>
              <span className="text-red-400 font-bold text-sm">
                {normalizeValue(mod.away_val, mod.id).toFixed(1)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
