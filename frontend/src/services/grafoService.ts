import api from './api';
import type { GraphData } from '../types';

export const grafoService = {
  async getGrafo(): Promise<GraphData> {
    const response = await api.get<GraphData>('/reportes/grafo');
    return response.data;
  },
};