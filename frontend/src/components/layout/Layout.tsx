import { useState, useEffect, useRef } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';
import { alertaService, type AlertaItem } from '../../services/alertaService';
import {
  LayoutDashboard,
  Users,
  FileText,
  Search,
  BarChart3,
  Network,
  Settings,
  LogOut,
  Shield,
  Bell,
  AlertTriangle,
  RefreshCw,
  X,
  Clock,
} from 'lucide-react';
import clsx from 'clsx';

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/clientes', icon: Users, label: 'Clientes' },
  { to: '/expedientes', icon: FileText, label: 'Expedientes' },
  { to: '/pep', icon: Search, label: 'Buscar PEP' },
  { to: '/reportes', icon: BarChart3, label: 'Reportes' },
  { to: '/grafo', icon: Network, label: 'Grafo de Relaciones' },
  { to: '/configuracion', icon: Settings, label: 'Configuracion' },
];

const NIVEL_ICONOS: Record<string, typeof AlertTriangle> = {
  alto: AlertTriangle,
  medio: Clock,
  bajo: AlertTriangle,
};

const NIVEL_COLORS: Record<string, string> = {
  alto: 'text-red-600 bg-red-50 border-red-200',
  medio: 'text-yellow-600 bg-yellow-50 border-yellow-200',
  bajo: 'text-blue-600 bg-blue-50 border-blue-200',
};

export default function Layout() {
  const { logout } = useAuthStore();
  const navigate = useNavigate();
  const [alertas, setAlertas] = useState<AlertaItem[]>([]);
  const [showAlertas, setShowAlertas] = useState(false);
  const [loadingAlertas, setLoadingAlertas] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchAlertas();
    const interval = setInterval(fetchAlertas, 60000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowAlertas(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const fetchAlertas = async () => {
    try {
      const data = await alertaService.listar(true);
      setAlertas(data);
    } catch {
      // silent
    }
  };

  const handleGenerarAlertas = async () => {
    setLoadingAlertas(true);
    try {
      await alertaService.generar();
      await fetchAlertas();
    } catch {
      // silent
    } finally {
      setLoadingAlertas(false);
    }
  };

  const handleMarcarLeida = async (alertaId: number) => {
    try {
      await alertaService.marcarLeida(alertaId);
      setAlertas(prev => prev.filter(a => a.id !== alertaId));
    } catch {
      // silent
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="h-16 flex items-center px-6 border-b border-gray-200">
          <Shield className="w-8 h-8 text-primary-600 mr-3" />
          <div>
            <h1 className="font-bold text-gray-900">Diligencia</h1>
            <p className="text-xs text-gray-500">Reforzada EDD</p>
          </div>
        </div>

        <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                clsx(
                  'flex items-center px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-100'
                )
              }
            >
              <item.icon className="w-5 h-5 mr-3" />
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-gray-200">
          <button
            onClick={handleLogout}
            className="flex items-center w-full px-3 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <LogOut className="w-5 h-5 mr-3" />
            Cerrar Sesion
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        {/* Top Bar */}
        <div className="sticky top-0 z-10 bg-white border-b border-gray-200 px-8 py-3 flex items-center justify-end">
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setShowAlertas(!showAlertas)}
              aria-label="Ver alertas"
              className="relative p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <Bell className="w-5 h-5 text-gray-600" />
              {alertas.length > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center font-medium">
                  {alertas.length > 9 ? '9+' : alertas.length}
                </span>
              )}
            </button>

            {showAlertas && (
              <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-xl border border-gray-200 max-h-96 overflow-hidden flex flex-col">
                <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
                  <h3 className="font-semibold text-sm">Alertas ({alertas.length})</h3>
                  <button
                    onClick={handleGenerarAlertas}
                    disabled={loadingAlertas}
                    className="text-xs text-primary-600 hover:text-primary-700 flex items-center"
                  >
                    <RefreshCw className={`w-3 h-3 mr-1 ${loadingAlertas ? 'animate-spin' : ''}`} />
                    Generar
                  </button>
                </div>
                <div className="overflow-y-auto flex-1">
                  {alertas.length === 0 ? (
                    <div className="px-4 py-8 text-center text-sm text-gray-400">
                      <Bell className="w-8 h-8 mx-auto mb-2 opacity-50" />
                      No hay alertas pendientes
                    </div>
                  ) : (
                    <div className="divide-y divide-gray-100">
                      {alertas.map((alerta) => {
                        const Icono = NIVEL_ICONOS[alerta.nivel] || AlertTriangle;
                        return (
                          <div
                            key={alerta.id}
                            className={clsx(
                              'px-4 py-3 flex items-start space-x-3 hover:bg-gray-50 transition-colors',
                              NIVEL_COLORS[alerta.nivel]?.split(' ')[1]
                            )}
                          >
                            <Icono className={clsx('w-5 h-5 mt-0.5 flex-shrink-0', NIVEL_COLORS[alerta.nivel]?.split(' ')[0])} />
                            <div className="flex-1 min-w-0">
                              <p className="text-sm text-gray-900">{alerta.mensaje}</p>
                              <p className="text-xs text-gray-400 mt-0.5">
                                {new Date(alerta.created_at).toLocaleString('es-PA')}
                              </p>
                            </div>
                            <button
                              onClick={() => handleMarcarLeida(alerta.id)}
                              className="p-1 hover:bg-gray-200 rounded flex-shrink-0"
                              aria-label="Marcar como leida"
                              title="Marcar como leida"
                            >
                              <X className="w-4 h-4 text-gray-400" />
                            </button>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
