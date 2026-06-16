import { useEffect, useState } from 'react';
import { reporteService } from '../services/reporteService';
import type { EventoAuditoria } from '../types';
import { Download, Filter, Clock, FileText } from 'lucide-react';

export default function ReportesPage() {
  const [auditoria, setAuditoria] = useState<EventoAuditoria[]>([]);
  const [loading, setLoading] = useState(true);
  const [expedienteFilter, setExpedienteFilter] = useState('');

  useEffect(() => {
    fetchAuditoria();
  }, []);

  const fetchAuditoria = async () => {
    setLoading(true);
    try {
      const data = await reporteService.getAuditoria(
        expedienteFilter ? Number(expedienteFilter) : undefined
      );
      setAuditoria(data);
    } catch (err) {
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const csv = await reporteService.exportarCSV();
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `expedientes_${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
    } catch (err) {
      console.error('Error:', err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reportes</h1>
          <p className="text-gray-500">Reportes y auditoria del sistema</p>
        </div>
        <button
          onClick={handleExport}
          className="btn-primary flex items-center"
        >
          <Download className="w-5 h-5 mr-2" />
          Exportar CSV
        </button>
      </div>

      {/* Auditoria */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold flex items-center">
            <Clock className="w-5 h-5 mr-2 text-primary-600" />
            Registro de Auditoria
          </h2>
          <div className="flex items-center space-x-3">
            <input
              type="text"
              placeholder="Filtrar por ID expediente"
              value={expedienteFilter}
              onChange={(e) => setExpedienteFilter(e.target.value)}
              className="input w-48"
            />
            <button onClick={fetchAuditoria} className="btn-secondary">
              <Filter className="w-4 h-4" />
            </button>
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : auditoria.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <FileText className="w-12 h-12 mx-auto mb-3" />
            <p>No hay registros de auditoria</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-sm text-gray-500 border-b">
                  <th className="pb-3 font-medium">Fecha/Hora</th>
                  <th className="pb-3 font-medium">Expediente</th>
                  <th className="pb-3 font-medium">Usuario</th>
                  <th className="pb-3 font-medium">Accion</th>
                  <th className="pb-3 font-medium">Detalles</th>
                </tr>
              </thead>
              <tbody className="text-sm">
                {auditoria.map((evento) => (
                  <tr key={evento.id} className="border-b last:border-0">
                    <td className="py-3 text-gray-500">
                      {new Date(evento.created_at).toLocaleString('es-PA')}
                    </td>
                    <td className="py-3 font-medium">
                      {evento.expediente_id || '-'}
                    </td>
                    <td className="py-3">{evento.usuario}</td>
                    <td className="py-3">
                      <span className="px-2 py-1 bg-gray-100 rounded text-xs font-medium">
                        {evento.accion}
                      </span>
                    </td>
                    <td className="py-3 text-gray-500 text-xs">
                      {evento.detalles ? JSON.stringify(evento.detalles) : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
