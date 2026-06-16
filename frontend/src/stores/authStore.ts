import { create } from 'zustand';
import { authService, LoginRequest } from '../services/authService';
import type { Usuario } from '../types';

interface AuthState {
  user: Usuario | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  login: (data: LoginRequest) => Promise<void>;
  logout: () => void;
  checkAuth: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: authService.isAuthenticated(),
  isLoading: false,
  error: null,

  login: async (data) => {
    set({ isLoading: true, error: null });
    try {
      await authService.login(data);
      const profile = await authService.getProfile();
      set({ user: profile, isAuthenticated: true, isLoading: false });
    } catch (err: any) {
      set({
        error: err.response?.data?.detail || 'Error al iniciar sesion',
        isLoading: false
      });
    }
  },

  logout: () => {
    authService.logout();
    set({ user: null, isAuthenticated: false });
  },

  checkAuth: () => {
    set({ isAuthenticated: authService.isAuthenticated() });
  },
}));