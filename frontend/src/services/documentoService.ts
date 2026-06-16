import api from './api';
import type { Documento } from '../types';

export const documentoService = {
  async upload(
    expedienteId: number,
    tipoDocumento: string,
    file: File
  ): Promise<Documento> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('tipo_documento', tipoDocumento);

    const response = await api.post<Documento>(
      `/documentos/${expedienteId}/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  async list(expedienteId: number): Promise<Documento[]> {
    const response = await api.get<Documento[]>(`/documentos/${expedienteId}/documentos`);
    return response.data;
  },

  async download(expedienteId: number, documentoId: number, filename: string): Promise<void> {
    const response = await api.get(
      `/documentos/${expedienteId}/download/${documentoId}`,
      { responseType: 'blob' }
    );
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
};
