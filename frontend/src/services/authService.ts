import api from './api';
import type { Usuario } from '../types';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  full_name?: string;
  rol: string;
}

export const authService = {
  async login(data: LoginRequest): Promise<LoginResponse> {
    const formData = new URLSearchParams();
    formData.append('username', data.username);
    formData.append('password', data.password);
    
    const response = await api.post<LoginResponse>('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    
    localStorage.setItem('access_token', response.data.access_token);
    return response.data;
  },

  async getProfile(): Promise<Usuario> {
    const response = await api.get<Usuario>('/auth/me');
    return response.data;
  },

  async register(data: RegisterRequest): Promise<Usuario> {
    const response = await api.post<Usuario>('/auth/register', data);
    return response.data;
  },

  logout() {
    localStorage.removeItem('access_token');
  },

  getToken(): string | null {
    return localStorage.getItem('access_token');
  },

  isAuthenticated(): boolean {
    return !!this.getToken();
  },
};
