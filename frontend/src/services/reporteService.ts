import api from './api';
import type { DashboardStats, EventoAuditoria } from '../types';

export const reporteService = {
  async getDashboard(): Promise<DashboardStats> {
    const response = await api.get<DashboardStats>('/reportes/dashboard');
    return response.data;
  },

  async getExpedientes(
    skip = 0,
    limit = 50,
    estado?: string,
    riesgo?: string
  ): Promise<unknown[]> {
    const response = await api.get('/reportes/expedientes', {
      params: { skip, limit, estado, riesgo },
    });
    return response.data;
  },

  async getAuditoria(
    expedienteId?: number,
    skip = 0,
    limit = 100
  ): Promise<EventoAuditoria[]> {
    const response = await api.get('/reportes/auditoria', {
      params: { expediente_id: expedienteId, skip, limit },
    });
    return response.data;
  },

  async exportarCSV(estado?: string): Promise<string> {
    const response = await api.get('/reportes/export/csv', {
      params: { estado },
    });
    return response.data;
  },
};
