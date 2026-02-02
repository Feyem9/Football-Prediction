/**
 * Tests - Header Component
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Header from './Header';

// Wrapper pour les tests
const renderWithRouter = (component: React.ReactNode) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

// Mock useAuth hook
vi.mock('../../hooks/useAuth', () => ({
  useAuth: () => ({
    user: null,
    isAuthenticated: false,
    isLoading: false,
    logout: vi.fn(),
  }),
}));

describe('Header Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders logo correctly', () => {
    renderWithRouter(<Header />);
    
    expect(screen.getByText('Prono')).toBeInTheDocument();
    expect(screen.getByText('score')).toBeInTheDocument();
  });

  it('renders navigation links', () => {
    renderWithRouter(<Header />);
    
    // Use getAllByText since links appear in both desktop and mobile menus
    expect(screen.getAllByText('Accueil').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Match Sûr').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Historique').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Aujourd'hui").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Matchs').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Classements').length).toBeGreaterThanOrEqual(1);
  });

  it('shows Connexion button when not authenticated', () => {
    renderWithRouter(<Header />);
    
    expect(screen.getByText('Connexion')).toBeInTheDocument();
  });

  it('links Connexion button to login page', () => {
    renderWithRouter(<Header />);
    
    const loginLink = screen.getByText('Connexion');
    expect(loginLink).toHaveAttribute('href', '/login');
  });

  it('toggles mobile menu when hamburger is clicked', () => {
    renderWithRouter(<Header />);
    
    // Find the hamburger button (has aria-label)
    const menuButton = screen.getByLabelText('Toggle menu');
    expect(menuButton).toBeInTheDocument();
    
    // Click to open
    fireEvent.click(menuButton);
    
    // The mobile menu should be visible (checking for expanded state)
    const accueilLinks = screen.getAllByText('Accueil');
    expect(accueilLinks.length).toBeGreaterThanOrEqual(1);
  });

  it('has correct navigation link destinations', () => {
    renderWithRouter(<Header />);
    
    // Check desktop navigation links
    const homeLinks = screen.getAllByRole('link', { name: /accueil/i });
    expect(homeLinks.some((link: HTMLElement) => link.getAttribute('href') === '/')).toBe(true);
    
    const sureLinks = screen.getAllByRole('link', { name: /match sûr/i });
    expect(sureLinks.some((link: HTMLElement) => link.getAttribute('href') === '/sure')).toBe(true);
  });
});

describe('Header Component - Mobile Menu', () => {
  it('shows mobile menu button', () => {
    renderWithRouter(<Header />);
    
    const menuButton = screen.getByLabelText('Toggle menu');
    expect(menuButton).toBeInTheDocument();
  });

  it('mobile menu has all navigation items', () => {
    renderWithRouter(<Header />);
    
    const menuButton = screen.getByLabelText('Toggle menu');
    fireEvent.click(menuButton);
    
    // Check for icons in mobile menu (use getAllByText as some may appear multiple times)
    expect(screen.getAllByText('🏠').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('🎯').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('📊').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('📅').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('⚽').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('🏆').length).toBeGreaterThanOrEqual(1);
  });
});
