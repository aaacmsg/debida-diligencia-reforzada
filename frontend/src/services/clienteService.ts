import api from './api';
import type { Cliente } from '../types';

export interface CreateClienteRequest {
  tipo_persona: 'natural' | 'juridica';
  nombre: string;
  apellido?: string;
  razon_social?: string;
  tipo_identificacion: 'cedula' | 'pasaporte' | 'ruc';
  numero_identificacion: string;
  fecha_nacimiento?: string;
  nacionalidad?: string;
  pais_residencia?: string;
  direccion?: string;
  telefono?: string;
  correo?: string;
  es_pep?: boolean;
  cargo_pep?: string;
  relacion_pep?: string;
  pais_residencia_fiscal?: string;
  actividad_economica?: string;
  sector_economico?: string;
  ingresos_anuales?: number;
  patrimonio?: number;
  origen_fondos?: string;
}

export const clienteService = {
  async list(skip = 0, limit = 100): Promise<Cliente[]> {
    const response = await api.get<Cliente[]>('/clientes/', { params: { skip, limit } });
    return response.data;
  },

  async get(id: number): Promise<Cliente> {
    const response = await api.get<Cliente>(`/clientes/${id}`);
    return response.data;
  },

  async create(data: CreateClienteRequest): Promise<Cliente> {
    const response = await api.post<Cliente>('/clientes/', data);
    return response.data;
  },

  async update(id: number, data: Partial<CreateClienteRequest>): Promise<Cliente> {
    const response = await api.put<Cliente>(`/clientes/${id}`, data);
    return response.data;
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/clientes/${id}`);
  },
};
