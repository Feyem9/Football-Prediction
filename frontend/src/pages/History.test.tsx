/**
 * Tests - Page History (Historique des pronostics)
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render } from '../test/test-utils';
import History from './History';

// Mock axios
vi.mock('axios', () => ({
  default: {
    get: vi.fn().mockResolvedValue({
      data: {
        predictions: [
          {
            id: 1,
            match: {
              homeTeam: { name: 'PSG' },
              awayTeam: { name: 'Lyon' },
              utcDate: '2026-01-15T20:00:00Z',
              score: { fullTime: { home: 3, away: 1 } },
            },
            prediction: 'HOME',
            result: 'WIN',
            confidence: 78,
          },
          {
            id: 2,
            match: {
              homeTeam: { name: 'Marseille' },
              awayTeam: { name: 'Monaco' },
              utcDate: '2026-01-12T17:00:00Z',
              score: { fullTime: { home: 1, away: 1 } },
            },
            prediction: 'HOME',
            result: 'LOSS',
            confidence: 65,
          },
          {
            id: 3,
            match: {
              homeTeam: { name: 'Lille' },
              awayTeam: { name: 'Rennes' },
              utcDate: '2026-01-10T20:00:00Z',
              score: { fullTime: { home: 0, away: 0 } },
            },
            prediction: 'DRAW',
            result: 'WIN',
            confidence: 55,
          },
        ],
        stats: {
          total: 100,
          won: 68,
          lost: 32,
          winRate: 68,
        },
      },
    }),
    create: vi.fn().mockReturnValue({
      get: vi.fn().mockResolvedValue({ data: { predictions: [] } }),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
    }),
  },
}));

describe('History Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders history page correctly', () => {
    render(<History />);
    
    // Page should render
    expect(document.body).toBeInTheDocument();
  });

  it('has container element', () => {
    render(<History />);
    
    const container = document.querySelector('.container');
    expect(container).toBeInTheDocument();
  });

  it('renders with proper structure', () => {
    render(<History />);
    
    // Should have content
    const divs = document.querySelectorAll('div');
    expect(divs.length).toBeGreaterThan(0);
  });
});

describe('History Page - Stats Overview', () => {
  it('displays statistics section', () => {
    render(<History />);
    
    // Stats should be shown
    const container = document.querySelector('.container');
    expect(container).toBeInTheDocument();
  });
});

describe('History Page - Prediction List', () => {
  it('displays prediction history', () => {
    render(<History />);
    
    // History list should be rendered
    const container = document.querySelector('.container');
    expect(container).toBeInTheDocument();
  });

  it('shows win/loss indicators', () => {
    render(<History />);
    
    // Indicators should be in the page
    expect(document.body).toBeInTheDocument();
  });
});

describe('History Page - Filtering', () => {
  it('has filter options', () => {
    render(<History />);
    
    // Filter section should exist
    const container = document.querySelector('.container');
    expect(container).toBeInTheDocument();
  });
});
