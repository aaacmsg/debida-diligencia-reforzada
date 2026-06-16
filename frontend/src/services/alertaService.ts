import api from './api';

export interface AlertaItem {
  id: number;
  expediente_id?: number;
  tipo_alerta: string;
  mensaje: string;
  nivel: string;
  leida: boolean;
  created_at: string;
}

export const alertaService = {
  async listar(soloNoLeidas = true): Promise<AlertaItem[]> {
    const response = await api.get<AlertaItem[]>('/alertas/', {
      params: { solo_no_leidas: soloNoLeidas },
    });
    return response.data;
  },

  async generar(): Promise<{ alertas_generadas: number }> {
    const response = await api.post('/alertas/generar');
    return response.data;
  },

  async marcarLeida(alertaId: number): Promise<void> {
    await api.post(`/alertas/${alertaId}/leer`);
  },
};
