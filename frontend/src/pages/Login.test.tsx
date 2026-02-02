/**
 * Tests - Page Login
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '../test/test-utils';
import Login from './Login';

// Mock useAuth hook
vi.mock('../hooks/useAuth', () => ({
  useAuth: () => ({
    login: vi.fn().mockResolvedValue({ success: true }),
    isLoading: false,
    error: null,
    clearError: vi.fn(),
  }),
}));

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('Login Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders login form correctly', () => {
    render(<Login />);
    
    expect(screen.getByText('Bon retour !')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('votre@email.com')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('••••••••')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /se connecter/i })).toBeInTheDocument();
  });

  it('shows email input with correct type', () => {
    render(<Login />);
    
    const emailInput = screen.getByPlaceholderText('votre@email.com');
    expect(emailInput).toHaveAttribute('type', 'email');
    expect(emailInput).toBeRequired();
  });

  it('shows password input with correct type', () => {
    render(<Login />);
    
    const passwordInput = screen.getByPlaceholderText('••••••••');
    expect(passwordInput).toHaveAttribute('type', 'password');
    expect(passwordInput).toBeRequired();
  });

  it('allows user to type in email field', () => {
    render(<Login />);
    
    const emailInput = screen.getByPlaceholderText('votre@email.com');
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    
    expect(emailInput).toHaveValue('test@example.com');
  });

  it('allows user to type in password field', () => {
    render(<Login />);
    
    const passwordInput = screen.getByPlaceholderText('••••••••');
    fireEvent.change(passwordInput, { target: { value: 'mypassword123' } });
    
    expect(passwordInput).toHaveValue('mypassword123');
  });

  it('shows link to registration page', () => {
    render(<Login />);
    
    // The link text is inside a span
    const registerLink = screen.getByRole('link', { name: /créer un compte/i });
    expect(registerLink).toHaveAttribute('href', '/register');
  });

  it('shows forgot password link', () => {
    render(<Login />);
    
    const forgotLink = screen.getByText(/mot de passe oublié/i);
    expect(forgotLink).toHaveAttribute('href', '/forgot-password');
  });

  it('shows trust badges', () => {
    render(<Login />);
    
    expect(screen.getByText('SSL Sécurisé')).toBeInTheDocument();
    expect(screen.getByText('RGPD Conforme')).toBeInTheDocument();
  });

  it('has proper page structure', () => {
    render(<Login />);
    
    // Page should have content
    const divs = document.querySelectorAll('div');
    expect(divs.length).toBeGreaterThan(0);
  });

  it('has submit button', () => {
    render(<Login />);
    
    const submitButton = screen.getByRole('button', { name: /se connecter/i });
    expect(submitButton).toHaveAttribute('type', 'submit');
  });
});
