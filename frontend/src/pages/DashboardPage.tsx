import { useEffect, useState } from 'react';
import { reporteService } from '../services/reporteService';
import { expedienteService } from '../services/expedienteService';
import type { DashboardStats, Expediente } from '../types';
import {
  FileText,
  AlertTriangle,
  CheckCircle,
  Clock,
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const ESTADO_COLORS: Record<string, string> = {
  borrador: '#94a3b8',
  pendiente_info: '#f59e0b',
  pendiente_revision: '#3b82f6',
  pendiente_gerencia: '#ef4444',
  aprobado: '#22c55e',
  rechazado: '#dc2626',
};

const RIESGO_COLORS: Record<string, string> = {
  bajo: '#22c55e',
  medio: '#eab308',
  alto: '#ef4444',
};

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentExpedientes, setRecentExpedientes] = useState<Expediente[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, expedientesData] = await Promise.all([
          reporteService.getDashboard(),
          expedienteService.list(0, 5),
        ]);
        setStats(statsData);
        setRecentExpedientes(expedientesData);
      } catch (err) {
        console.error('Error fetching dashboard:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const estadoData = stats 
    ? Object.entries(stats.por_estado).map(([name, value]) => ({
        name: name.replace('_', ' '),
        value,
        fill: ESTADO_COLORS[name] || '#94a3b8',
      }))
    : [];

  const riesgoData = stats
    ? Object.entries(stats.por_riesgo).map(([name, value]) => ({
        name,
        value,
        fill: RIESGO_COLORS[name] || '#94a3b8',
      }))
    : [];

  const statCards = [
    { label: 'Total Expedientes', value: stats?.total_expedientes || 0, icon: FileText, color: 'text-primary-600' },
    { label: 'Pendientes Revision', value: stats?.por_estado?.pendiente_revision || 0, icon: Clock, color: 'text-blue-600' },
    { label: 'Alto Riesgo', value: stats?.por_riesgo?.alto || 0, icon: AlertTriangle, color: 'text-red-600' },
    { label: 'Aprobados', value: stats?.por_estado?.aprobado || 0, icon: CheckCircle, color: 'text-green-600' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500">Resumen del sistema de Diligencia Reforzada</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card) => (
          <div key={card.label} className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{card.label}</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{card.value}</p>
              </div>
              <div className={`p-3 rounded-full bg-gray-50 ${card.color}`}>
                <card.icon className="w-6 h-6" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Estado Chart */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Expedientes por Estado</h3>
          <div className="h-64">
            {estadoData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={estadoData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {estadoData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-400">
                No hay datos disponibles
              </div>
            )}
          </div>
        </div>

        {/* Riesgo Chart */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Expedientes por Nivel de Riesgo</h3>
          <div className="h-64">
            {riesgoData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={riesgoData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="name" type="category" width={80} />
                  <Tooltip />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                    {riesgoData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-400">
                No hay datos disponibles
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Expedientes */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Expedientes Recientes</h3>
          <a href="/expedientes" className="text-primary-600 text-sm hover:underline">
            Ver todos
          </a>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-sm text-gray-500 border-b">
                <th className="pb-3 font-medium">Numero</th>
                <th className="pb-3 font-medium">Estado</th>
                <th className="pb-3 font-medium">Nivel Riesgo</th>
                <th className="pb-3 font-medium">Fecha</th>
              </tr>
            </thead>
            <tbody className="text-sm">
              {recentExpedientes.map((exp) => (
                <tr key={exp.id} className="border-b last:border-0">
                  <td className="py-3 font-medium">{exp.numero_expediente}</td>
                  <td className="py-3">
                    <span 
                      className="px-2 py-1 rounded-full text-xs font-medium"
                      style={{ 
                        backgroundColor: `${ESTADO_COLORS[exp.estado]}20`,
                        color: ESTADO_COLORS[exp.estado]
                      }}
                    >
                      {exp.estado.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="py-3">
                    <span 
                      className="px-2 py-1 rounded-full text-xs font-medium capitalize"
                      style={{ 
                        backgroundColor: `${RIESGO_COLORS[exp.nivel_riesgo]}20`,
                        color: RIESGO_COLORS[exp.nivel_riesgo]
                      }}
                    >
                      {exp.nivel_riesgo}
                    </span>
                  </td>
                  <td className="py-3 text-gray-500">
                    {new Date(exp.created_at).toLocaleDateString('es-PA')}
                  </td>
                </tr>
              ))}
              {recentExpedientes.length === 0 && (
                <tr>
                  <td colSpan={4} className="py-6 text-center text-gray-400">
                    No hay expedientes recientes
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
