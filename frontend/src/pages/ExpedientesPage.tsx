import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { expedienteService } from '../services/expedienteService';
import type { Expediente } from '../types';
import { FileText, Filter, ChevronRight } from 'lucide-react';
import clsx from 'clsx';

const ESTADO_COLORS: Record<string, string> = {
  borrador: 'bg-gray-100 text-gray-700',
  pendiente_info: 'bg-yellow-100 text-yellow-700',
  pendiente_revision: 'bg-blue-100 text-blue-700',
  pendiente_gerencia: 'bg-red-100 text-red-700',
  aprobado: 'bg-green-100 text-green-700',
  rechazado: 'bg-red-100 text-red-700',
};

const RIESGO_COLORS: Record<string, string> = {
  bajo: 'bg-green-100 text-green-700',
  medio: 'bg-yellow-100 text-yellow-700',
  alto: 'bg-red-100 text-red-700',
};

const ESTADOS = ['borrador', 'pendiente_info', 'pendiente_revision', 'pendiente_gerencia', 'aprobado', 'rechazado'];
const RIESGOS = ['bajo', 'medio', 'alto'];

export default function ExpedientesPage() {
  const [expedientes, setExpedientes] = useState<Expediente[]>([]);
  const [loading, setLoading] = useState(true);
  const [filtroEstado, setFiltroEstado] = useState<string>('');
  const [filtroRiesgo, setFiltroRiesgo] = useState<string>('');

  useEffect(() => {
    fetchExpedientes();
  }, [filtroEstado, filtroRiesgo]);

  const fetchExpedientes = async () => {
    setLoading(true);
    try {
      const data = await expedienteService.list(
        0, 100,
        filtroEstado || undefined,
        filtroRiesgo || undefined
      );
      setExpedientes(data);
    } catch (err) {
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Expedientes</h1>
          <p className="text-gray-500">Gestion y seguimiento de expedientes EDD</p>
        </div>
      </div>

      {/* Filtros */}
      <div className="card">
        <div className="flex items-center space-x-4">
          <Filter className="w-5 h-5 text-gray-400" />
          
          <select
            value={filtroEstado}
            onChange={(e) => setFiltroEstado(e.target.value)}
            className="input w-48"
          >
            <option value="">Todos los estados</option>
            {ESTADOS.map((estado) => (
              <option key={estado} value={estado}>
                {estado.replace('_', ' ')}
              </option>
            ))}
          </select>

          <select
            value={filtroRiesgo}
            onChange={(e) => setFiltroRiesgo(e.target.value)}
            className="input w-48"
          >
            <option value="">Todos los riesgos</option>
            {RIESGOS.map((riesgo) => (
              <option key={riesgo} value={riesgo}>
                {riesgo.charAt(0).toUpperCase() + riesgo.slice(1)}
              </option>
            ))}
          </select>

          {(filtroEstado || filtroRiesgo) && (
            <button
              onClick={() => {
                setFiltroEstado('');
                setFiltroRiesgo('');
              }}
              className="text-sm text-primary-600 hover:underline"
            >
              Limpiar filtros
            </button>
          )}
        </div>
      </div>

      {/* Lista */}
      <div className="space-y-3">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : expedientes.length === 0 ? (
          <div className="card text-center py-12">
            <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No se encontraron expedientes</p>
          </div>
        ) : (
          expedientes.map((exp) => (
            <Link
              key={exp.id}
              to={`/expedientes/${exp.id}`}
              className="card flex items-center justify-between hover:shadow-md transition-shadow"
            >
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-primary-50 rounded-lg">
                  <FileText className="w-6 h-6 text-primary-600" />
                </div>
                <div>
                  <p className="font-semibold text-gray-900">{exp.numero_expediente}</p>
                  <p className="text-sm text-gray-500">
                    Cliente ID: {exp.cliente_id}
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <span className={clsx('px-3 py-1 rounded-full text-xs font-medium capitalize', ESTADO_COLORS[exp.estado])}>
                  {exp.estado.replace('_', ' ')}
                </span>
                <span className={clsx('px-3 py-1 rounded-full text-xs font-medium capitalize', RIESGO_COLORS[exp.nivel_riesgo])}>
                  {exp.nivel_riesgo}
                </span>
                {exp.score_riesgo !== null && exp.score_riesgo !== undefined && (
                  <span className="text-sm text-gray-500">
                    Score: {exp.score_riesgo.toFixed(0)}
                  </span>
                )}
                <ChevronRight className="w-5 h-5 text-gray-400" />
              </div>
            </Link>
          ))
        )}
      </div>
    </div>
  );
}
