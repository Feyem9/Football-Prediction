/**
 * Hook d'authentification - Gestion JWT avec refresh token
 */
import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_URL = `${API_BASE}/api/v1`;

interface User {
  id: number;
  email: string;
  username: string;
  email_verified: boolean;
  created_at: string;
}

interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData {
  email: string;
  username: string;
  password: string;
}

// Axios instance avec interceptors
const authApi = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' }
});

// Interceptor pour ajouter le token
authApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor pour refresh automatique
authApi.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/auth/refresh`, {
            refresh_token: refreshToken
          });
          
          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);
          
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return authApi(originalRequest);
        }
      } catch {
        // Refresh failed, logout
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
    error: null
  });

  // Vérifier le token au chargement
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        setState(prev => ({ ...prev, isLoading: false }));
        return;
      }

      try {
        const response = await authApi.get('/auth/me');
        setState({
          user: response.data,
          isAuthenticated: true,
          isLoading: false,
          error: null
        });
      } catch {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setState({
          user: null,
          isAuthenticated: false,
          isLoading: false,
          error: null
        });
      }
    };

    checkAuth();
  }, []);

  // Login
  const login = useCallback(async (credentials: LoginCredentials) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await axios.post<AuthTokens>(`${API_URL}/auth/login`, credentials);
      const { access_token, refresh_token } = response.data;

      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);

      // Récupérer les infos utilisateur
      const userResponse = await authApi.get('/auth/me');
      
      setState({
        user: userResponse.data,
        isAuthenticated: true,
        isLoading: false,
        error: null
      });

      return { success: true };
    } catch (error: unknown) {
      const axiosError = error as { response?: { data?: { detail?: string } } };
      const message = axiosError.response?.data?.detail || 'Erreur de connexion';
      setState(prev => ({ ...prev, isLoading: false, error: message }));
      return { success: false, error: message };
    }
  }, []);

  // Register
  const register = useCallback(async (data: RegisterData) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      await axios.post(`${API_URL}/auth/register`, data);
      
      setState(prev => ({ ...prev, isLoading: false }));
      return { success: true, message: 'Compte créé ! Vérifiez votre email.' };
    } catch (error: unknown) {
      const axiosError = error as { response?: { data?: { detail?: string } } };
      const message = axiosError.response?.data?.detail || 'Erreur lors de l\'inscription';
      setState(prev => ({ ...prev, isLoading: false, error: message }));
      return { success: false, error: message };
    }
  }, []);

  // Logout
  const logout = useCallback(async () => {
    try {
      await authApi.post('/auth/logout');
    } catch {
      // Continue logout even if API call fails
    }

    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    
    setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null
    });
  }, []);

  // Forgot Password
  const forgotPassword = useCallback(async (email: string) => {
    try {
      await axios.post(`${API_URL}/auth/forgot-password`, { email });
      return { success: true, message: 'Email de réinitialisation envoyé !' };
    } catch (error: unknown) {
      const axiosError = error as { response?: { data?: { detail?: string } } };
      const message = axiosError.response?.data?.detail || 'Erreur lors de l\'envoi';
      return { success: false, error: message };
    }
  }, []);

  // Clear Error
  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    ...state,
    login,
    register,
    logout,
    forgotPassword,
    clearError
  };
}

export { authApi };
