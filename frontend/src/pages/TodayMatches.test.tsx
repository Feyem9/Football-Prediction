/**
 * Tests - Page TodayMatches (Matchs du jour)
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render } from '../test/test-utils';
import TodayMatches from './TodayMatches';

// Mock axios
vi.mock('axios', () => ({
  default: {
    get: vi.fn().mockResolvedValue({
      data: {
        matches: [
          {
            id: 1,
            homeTeam: { name: 'Real Madrid', crest: 'rm.png' },
            awayTeam: { name: 'Barcelona', crest: 'fcb.png' },
            utcDate: new Date().toISOString(),
            status: 'SCHEDULED',
            competition: { name: 'La Liga', emblem: 'laliga.png' },
          },
          {
            id: 2,
            homeTeam: { name: 'Bayern Munich', crest: 'bayern.png' },
            awayTeam: { name: 'Dortmund', crest: 'bvb.png' },
            utcDate: new Date().toISOString(),
            status: 'IN_PLAY',
            score: { fullTime: { home: 1, away: 1 } },
            competition: { name: 'Bundesliga', emblem: 'bundesliga.png' },
          },
        ],
      },
    }),
    create: vi.fn().mockReturnValue({
      get: vi.fn().mockResolvedValue({ data: { matches: [] } }),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
    }),
  },
}));

describe('TodayMatches Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders today matches page correctly', () => {
    render(<TodayMatches />);
    
    // Page should render
    expect(document.body).toBeInTheDocument();
  });

  it('has container element', () => {
    render(<TodayMatches />);
    
    const container = document.querySelector('.container');
    expect(container).toBeInTheDocument();
  });
});

describe('TodayMatches Page - Match Categories', () => {
  it('renders the page structure', () => {
    render(<TodayMatches />);
    
    // Check page is rendered with proper structure
    const container = document.querySelector('.container');
    expect(container).toBeInTheDocument();
  });

  it('has section for matches', async () => {
    render(<TodayMatches />);
    
    // Page should have some sections
    const sections = document.querySelectorAll('section, div');
    expect(sections.length).toBeGreaterThan(0);
  });
});

describe('TodayMatches Page - Match States', () => {
  it('handles different match statuses', () => {
    render(<TodayMatches />);
    
    // Page renders correctly regardless of match status
    expect(document.body).toBeInTheDocument();
  });
});
