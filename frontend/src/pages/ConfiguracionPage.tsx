import { useState, useEffect } from 'react';
import { Settings, Database, Shield, Bell, Loader2, Save } from 'lucide-react';
import api from '../services/api';
import toast from 'react-hot-toast';

export default function ConfiguracionPage() {
  const [syncing, setSyncing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [config, setConfig] = useState<Record<string, string>>({});

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    setLoading(true);
    try {
      const response = await api.get('/configuracion/');
      setConfig(response.data);
    } catch {
      setConfig({});
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      const response = await api.post('/pep/sincronizar');
      const data = response.data;
      toast.success(
        `Sincronizados ${data.sincronizados} nuevos. Total: ${data.total_funcionarios} funcionarios`
      );
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al sincronizar');
    } finally {
      setSyncing(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.put('/configuracion/', config);
      toast.success('Configuracion guardada');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al guardar configuracion');
    } finally {
      setSaving(false);
    }
  };

  const updateConfig = (clave: string, valor: string) => {
    setConfig(prev => ({ ...prev, [clave]: valor }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const cfg = (key: string, fallback: string) => config[key] || fallback;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Configuracion</h1>
          <p className="text-gray-500">Ajustes del sistema</p>
        </div>
        <button
          onClick={handleSave}
          disabled={saving}
          className="btn-primary flex items-center"
        >
          {saving ? (
            <Loader2 className="w-5 h-5 mr-2 animate-spin" />
          ) : (
            <Save className="w-5 h-5 mr-2" />
          )}
          Guardar Cambios
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Datos PEP */}
        <div className="card">
          <div className="flex items-center mb-4">
            <Database className="w-5 h-5 mr-2 text-primary-600" />
            <h2 className="font-semibold">Datos de Funcionarios Publicos</h2>
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <p className="font-medium">Ultima sincronizacion</p>
                <p className="text-sm text-gray-500">Nunca</p>
              </div>
              <button
                onClick={handleSync}
                disabled={syncing}
                className="btn-secondary text-sm flex items-center"
              >
                {syncing ? (
                  <><Loader2 className="w-4 h-4 mr-1 animate-spin" />Sincronizando...</>
                ) : (
                  'Sincronizar Ahora'
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Seguridad */}
        <div className="card">
          <div className="flex items-center mb-4">
            <Shield className="w-5 h-5 mr-2 text-primary-600" />
            <h2 className="font-semibold">Seguridad</h2>
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <p className="font-medium">Tiempo de expiracion de sesion</p>
                <p className="text-sm text-gray-500">Minutos</p>
              </div>
              <input
                type="number"
                value={cfg('access_token_expire_minutes', '60')}
                onChange={(e) => updateConfig('access_token_expire_minutes', e.target.value)}
                className="input w-20 text-center"
              />
            </div>
          </div>
        </div>

        {/* Notificaciones */}
        <div className="card">
          <div className="flex items-center mb-4">
            <Bell className="w-5 h-5 mr-2 text-primary-600" />
            <h2 className="font-semibold">Notificaciones</h2>
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <p className="font-medium">Alertas de documentacion</p>
                <p className="text-sm text-gray-500">Notificar cuando expire</p>
              </div>
              <input
                type="checkbox"
                className="w-5 h-5"
                checked={cfg('alertas_documentacion', 'true') === 'true'}
                onChange={(e) => updateConfig('alertas_documentacion', e.target.checked.toString())}
              />
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <p className="font-medium">Alertas de alto riesgo</p>
                <p className="text-sm text-gray-500">Notificar expedientes de alto riesgo</p>
              </div>
              <input
                type="checkbox"
                className="w-5 h-5"
                checked={cfg('alertas_alto_riesgo', 'true') === 'true'}
                onChange={(e) => updateConfig('alertas_alto_riesgo', e.target.checked.toString())}
              />
            </div>
          </div>
        </div>

        {/* Parametros de Riesgo */}
        <div className="card">
          <div className="flex items-center mb-4">
            <Settings className="w-5 h-5 mr-2 text-primary-600" />
            <h2 className="font-semibold">Parametros de Riesgo</h2>
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <p className="font-medium">Umbral Beneficiario Final</p>
                <p className="text-sm text-gray-500">Porcentaje minimo de participacion</p>
              </div>
              <input
                type="number"
                value={cfg('umbral_beneficiario', '10')}
                onChange={(e) => updateConfig('umbral_beneficiario', e.target.value)}
                className="input w-20 text-center"
              />
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <p className="font-medium">Threshold Fuzzy Matching</p>
                <p className="text-sm text-gray-500">Porcentaje para coincidencias PEP</p>
              </div>
              <input
                type="number"
                value={cfg('fuzzy_match_threshold', '85')}
                onChange={(e) => updateConfig('fuzzy_match_threshold', e.target.value)}
                className="input w-20 text-center"
              />
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <p className="font-medium">Retencion de datos</p>
                <p className="text-sm text-gray-500">Anos minima de conservacion</p>
              </div>
              <input
                type="number"
                value={cfg('retention_years', '5')}
                onChange={(e) => updateConfig('retention_years', e.target.value)}
                className="input w-20 text-center"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="card bg-yellow-50 border-yellow-200">
        <p className="text-sm text-yellow-800">
          <strong>Nota:</strong> Los cambios en la configuracion pueden afectar el comportamiento
          del sistema. Asegurese de documentar cualquier modificacion para auditoria.
        </p>
      </div>
    </div>
  );
}
