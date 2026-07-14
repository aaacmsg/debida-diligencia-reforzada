import api from './api';
import type { Expediente, ExpedienteDetalle, EventoAuditoria } from '../types';

export interface CreateExpedienteRequest {
  cliente_id: number;
  nivel_riesgo?: 'bajo' | 'medio' | 'alto';
  score_riesgo?: number;
  variables_riesgo?: Record<string, unknown>;
}

export interface UpdateExpedienteRequest {
  nivel_riesgo?: 'bajo' | 'medio' | 'alto';
  score_riesgo?: number;
  variables_riesgo?: Record<string, unknown>;
  estado?: string;
  comentario_aprobacion?: string;
}

export const expedienteService = {
  async list(
    skip = 0,
    limit = 100,
    estado?: string,
    nivel_riesgo?: string
  ): Promise<Expediente[]> {
    const response = await api.get<Expediente[]>('/expedientes/', {
      params: { skip, limit, estado, nivel_riesgo },
    });
    return response.data;
  },

  async get(id: number): Promise<ExpedienteDetalle> {
    const response = await api.get<ExpedienteDetalle>(`/expedientes/${id}`);
    return response.data;
  },

  async create(data: CreateExpedienteRequest): Promise<Expediente> {
    const response = await api.post<Expediente>('/expedientes/', data);
    return response.data;
  },

  async update(id: number, data: UpdateExpedienteRequest): Promise<Expediente> {
    const response = await api.put<Expediente>(`/expedientes/${id}`, data);
    return response.data;
  },

  async aprobar(id: number, comentario: string): Promise<Expediente> {
    const response = await api.post<Expediente>(`/expedientes/${id}/aprobar`, null, {
      params: { comentario },
    });
    return response.data;
  },

  async rechazar(id: number, comentario: string): Promise<Expediente> {
    const response = await api.post<Expediente>(`/expedientes/${id}/rechazar`, null, {
      params: { comentario },
    });
    return response.data;
  },

  async exportarPdf(id: number, numeroExpediente: string): Promise<void> {
    const response = await api.get<Blob>(`/expedientes/${id}/pdf`, {
      responseType: 'blob',
    });
    const url = window.URL.createObjectURL(response.data);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${numeroExpediente}.pdf`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },

  async getAuditoria(id: number): Promise<EventoAuditoria[]> {
    const response = await api.get<EventoAuditoria[]>(`/reportes/auditoria`, {
      params: { expediente_id: id },
    });
    return response.data;
  },
};
