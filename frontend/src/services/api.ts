import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

const API_URL = import.meta.env.VITE_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

interface RefreshResponse {
  access_token: string;
  refresh_token?: string;
}

// Una sola llamada de refresh compartida aunque fallen varias requests a la vez
let refreshPromise: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  const refreshToken = localStorage.getItem('refresh_token');
  if (!refreshToken) {
    throw new Error('Sin refresh token');
  }
  // axios "crudo" para no pasar por los interceptors de esta instancia
  const response = await axios.post<RefreshResponse>(`${API_URL}/auth/refresh`, {
    refresh_token: refreshToken,
  });
  localStorage.setItem('access_token', response.data.access_token);
  if (response.data.refresh_token) {
    localStorage.setItem('refresh_token', response.data.refresh_token);
  }
  return response.data.access_token;
}

function limpiarSesionYRedirigir(): void {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  window.location.href = '/login';
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as
      | (InternalAxiosRequestConfig & { _retry?: boolean })
      | undefined;
    const esLlamadaAuth =
      original?.url?.includes('/auth/login') || original?.url?.includes('/auth/refresh');

    if (error.response?.status === 401 && original && !original._retry && !esLlamadaAuth) {
      original._retry = true;
      try {
        refreshPromise = refreshPromise ?? refreshAccessToken();
        const token = await refreshPromise;
        refreshPromise = null;
        original.headers.Authorization = `Bearer ${token}`;
        return api(original);
      } catch {
        refreshPromise = null;
        limpiarSesionYRedirigir();
      }
    } else if (error.response?.status === 401 && !esLlamadaAuth) {
      limpiarSesionYRedirigir();
    }
    return Promise.reject(error);
  }
);

export default api;
