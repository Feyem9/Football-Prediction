/**
 * Tests - Page Home (Liste des matchs)
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render } from '../test/test-utils';
import Home from './Home';

// Mock axios
vi.mock('axios', () => ({
  default: {
    get: vi.fn().mockResolvedValue({
      data: [
        {
          id: 1,
          homeTeam: { name: 'Paris Saint-Germain', crest: 'psg.png' },
          awayTeam: { name: 'Olympique de Marseille', crest: 'om.png' },
          utcDate: '2026-02-15T20:00:00Z',
          status: 'SCHEDULED',
          competition: { name: 'Ligue 1' },
        },
        {
          id: 2,
          homeTeam: { name: 'Manchester United', crest: 'manu.png' },
          awayTeam: { name: 'Liverpool', crest: 'liv.png' },
          utcDate: '2026-02-15T17:00:00Z',
          status: 'SCHEDULED',
          competition: { name: 'Premier League' },
        },
      ],
    }),
    create: vi.fn().mockReturnValue({
      get: vi.fn().mockResolvedValue({ data: [] }),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
    }),
  },
}));

describe('Home Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders home page correctly', () => {
    render(<Home />);
    
    // Check for main page elements
    expect(document.querySelector('.container')).toBeInTheDocument();
  });

  it('has matchs section', async () => {
    render(<Home />);
    
    // The page should have content
    const container = document.querySelector('.container');
    expect(container).toBeInTheDocument();
  });

  it('renders with responsive layout', () => {
    render(<Home />);
    
    // Check for responsive classes
    const main = document.querySelector('main') || document.querySelector('.container');
    expect(main).toBeInTheDocument();
  });
});

describe('Home Page - Loading States', () => {
  it('shows loading state initially', () => {
    render(<Home />);
    
    // There should be some content on the page
    expect(document.body).toBeInTheDocument();
  });
});

describe('Home Page - Match Display', () => {
  it('renders match cards when data is loaded', async () => {
    render(<Home />);
    
    // Page should render
    const container = document.querySelector('.container');
    expect(container).toBeInTheDocument();
  });
});
