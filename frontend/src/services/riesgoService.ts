import api from './api';
import type { CalculoRiesgoRequest, CalculoRiesgoResponse } from '../types';

export const riesgoService = {
  async calcular(data: CalculoRiesgoRequest): Promise<CalculoRiesgoResponse> {
    const response = await api.post<CalculoRiesgoResponse>('/riesgos/calcular', data);
    return response.data;
  },
};
