import api from './api';
import type { BeneficiarioFinal, BeneficiarioFinalCreate } from '../types';

export const beneficiarioService = {
  async list(clienteId: number): Promise<BeneficiarioFinal[]> {
    const response = await api.get<BeneficiarioFinal[]>(`/beneficiarios/${clienteId}`);
    return response.data;
  },

  async create(clienteId: number, data: BeneficiarioFinalCreate): Promise<BeneficiarioFinal> {
    const response = await api.post<BeneficiarioFinal>(`/beneficiarios/${clienteId}`, data);
    return response.data;
  },

  async delete(clienteId: number, beneficiarioId: number): Promise<void> {
    await api.delete(`/beneficiarios/${clienteId}/${beneficiarioId}`);
  },
};
