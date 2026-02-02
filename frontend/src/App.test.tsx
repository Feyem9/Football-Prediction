/**
 * Tests - App Component
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from './App';

// Mock all page components
vi.mock('./pages/Home', () => ({
  default: () => <div data-testid="home-page">Home Page</div>,
}));

vi.mock('./pages/Login', () => ({
  default: () => <div data-testid="login-page">Login Page</div>,
}));

vi.mock('./pages/Register', () => ({
  default: () => <div data-testid="register-page">Register Page</div>,
}));

vi.mock('./pages/Profile', () => ({
  default: () => <div data-testid="profile-page">Profile Page</div>,
}));

vi.mock('./pages/TodayMatches', () => ({
  default: () => <div data-testid="today-page">Today Matches</div>,
}));

vi.mock('./pages/MatchDetail', () => ({
  default: () => <div data-testid="match-detail-page">Match Detail</div>,
}));

vi.mock('./pages/Standings', () => ({
  default: () => <div data-testid="standings-page">Standings</div>,
}));

vi.mock('./pages/SureMatch', () => ({
  default: () => <div data-testid="sure-page">Sure Match</div>,
}));

vi.mock('./pages/History', () => ({
  default: () => <div data-testid="history-page">History</div>,
}));

vi.mock('./components/layout/Header', () => ({
  default: () => <header data-testid="header">Header</header>,
}));

describe('App Component', () => {
  it('renders without crashing', () => {
    render(<App />);
    
    expect(screen.getByTestId('header')).toBeInTheDocument();
  });

  it('renders header component', () => {
    render(<App />);
    
    expect(screen.getByTestId('header')).toBeInTheDocument();
  });

  it('renders footer with copyright', () => {
    render(<App />);
    
    expect(screen.getByText(/Pronoscore 2026/i)).toBeInTheDocument();
  });

  it('renders home page by default', () => {
    render(<App />);
    
    expect(screen.getByTestId('home-page')).toBeInTheDocument();
  });

  it('has correct structure with header and main', () => {
    render(<App />);
    
    const header = screen.getByTestId('header');
    expect(header).toBeInTheDocument();
    
    // Check for main content area
    const main = document.querySelector('main');
    expect(main).toBeInTheDocument();
  });

  it('renders footer text', () => {
    render(<App />);
    
    expect(screen.getByText(/Prédictions basées sur 3 logiques familiales/i)).toBeInTheDocument();
  });

  it('shows API info in footer', () => {
    render(<App />);
    
    expect(screen.getByText(/football-prediction-mbil.onrender.com/i)).toBeInTheDocument();
  });
});

describe('App Routes', () => {
  it('defines route for home page', () => {
    render(<App />);
    
    // Home is the default route
    expect(screen.getByTestId('home-page')).toBeInTheDocument();
  });
});
