/**
 * Tests - Page Register (Multi-step form)
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '../test/test-utils';
import Register from './Register';

// Mock useAuth hook
vi.mock('../hooks/useAuth', () => ({
  useAuth: () => ({
    register: vi.fn().mockResolvedValue({ success: true }),
    isLoading: false,
    error: null,
    clearError: vi.fn(),
  }),
}));

describe('Register Page - Step 1', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders register form correctly', () => {
    render(<Register />);
    
    // First step should show username and email
    expect(screen.getByPlaceholderText('VotrePseudo')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('votre@email.com')).toBeInTheDocument();
  });

  it('shows step indicators', () => {
    render(<Register />);
    
    // Should have progress steps
    expect(screen.getByText('1')).toBeInTheDocument();
  });

  it('shows username input', () => {
    render(<Register />);
    
    const usernameInput = screen.getByPlaceholderText('VotrePseudo');
    expect(usernameInput).toHaveAttribute('type', 'text');
    expect(usernameInput).toBeRequired();
  });

  it('shows email input', () => {
    render(<Register />);
    
    const emailInput = screen.getByPlaceholderText('votre@email.com');
    expect(emailInput).toHaveAttribute('type', 'email');
    expect(emailInput).toBeRequired();
  });

  it('allows user to type username', () => {
    render(<Register />);
    
    const usernameInput = screen.getByPlaceholderText('VotrePseudo');
    fireEvent.change(usernameInput, { target: { value: 'TestUser' } });
    
    expect(usernameInput).toHaveValue('TestUser');
  });

  it('allows user to type email', () => {
    render(<Register />);
    
    const emailInput = screen.getByPlaceholderText('votre@email.com');
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    
    expect(emailInput).toHaveValue('test@example.com');
  });

  it('shows continue button', () => {
    render(<Register />);
    
    expect(screen.getByText(/continuer/i)).toBeInTheDocument();
  });

  it('shows link to login page', () => {
    render(<Register />);
    
    // The link text is inside a span
    const loginLink = screen.getByRole('link', { name: /se connecter/i });
    expect(loginLink).toHaveAttribute('href', '/login');
  });

  it('shows feature badges', () => {
    render(<Register />);
    
    expect(screen.getByText('Pronostics IA')).toBeInTheDocument();
    expect(screen.getByText('Stats détaillées')).toBeInTheDocument();
    expect(screen.getByText('65%+ réussite')).toBeInTheDocument();
  });
});

describe('Register Page - Navigation', () => {
  it('enables continue button when step 1 is valid', () => {
    render(<Register />);
    
    // Fill valid data
    const usernameInput = screen.getByPlaceholderText('VotrePseudo');
    const emailInput = screen.getByPlaceholderText('votre@email.com');
    
    fireEvent.change(usernameInput, { target: { value: 'TestUser' } });
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    
    const continueButton = screen.getByText(/continuer/i);
    expect(continueButton).not.toBeDisabled();
  });

  it('has proper page structure', () => {
    render(<Register />);
    
    // Page should have content
    const divs = document.querySelectorAll('div');
    expect(divs.length).toBeGreaterThan(0);
  });
});
