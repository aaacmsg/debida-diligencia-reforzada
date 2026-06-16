import api from './api';
import type { PEPSearchResult } from '../types';

export interface PEPSearchRequest {
  nombre?: string;
  apellido?: string;
  cedula?: string;
}

export interface CargoCategoria {
  categoria: string;
  cargos: string[];
}

export const pepService = {
  async buscar(data: PEPSearchRequest): Promise<PEPSearchResult[]> {
    const response = await api.post<PEPSearchResult[]>('/pep/buscar', data);
    return response.data;
  },

  async getEstadisticas(): Promise<{
    total_funcionarios: number;
    clasificados_pep: number;
  }> {
    const response = await api.get('/pep/funcionarios/count');
    return response.data;
  },

  async getCargos(): Promise<CargoCategoria[]> {
    const response = await api.get<CargoCategoria[]>('/pep/cargos');
    return response.data;
  },
};
