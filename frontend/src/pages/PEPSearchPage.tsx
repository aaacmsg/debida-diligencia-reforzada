import { useState, useEffect } from 'react';
import { pepService, type CargoCategoria } from '../services/pepService';
import type { PEPSearchResult } from '../types';
import { Search, User, Building, AlertTriangle, CheckCircle, Loader2, ChevronDown, ChevronUp, Scale } from 'lucide-react';
import clsx from 'clsx';

export default function PEPSearchPage() {
  const [nombre, setNombre] = useState('');
  const [apellido, setApellido] = useState('');
  const [cedula, setCedula] = useState('');
  const [resultados, setResultados] = useState<PEPSearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [buscado, setBuscado] = useState(false);
  const [stats, setStats] = useState<{ total_funcionarios: number; clasificados_pep: number } | null>(null);
  const [showCargos, setShowCargos] = useState(false);
  const [cargosPEP, setCargosPEP] = useState<CargoCategoria[]>([]);

  useEffect(() => {
    pepService.getCargos().then(setCargosPEP).catch(console.error);
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!nombre && !apellido && !cedula) {
      return;
    }

    setLoading(true);
    setBuscado(true);
    try {
      const data = await pepService.buscar({ nombre, apellido, cedula });
      setResultados(data);

      if (!stats) {
        const statsData = await pepService.getEstadisticas();
        setStats(statsData);
      }
    } catch (err) {
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 95) return 'text-red-600 bg-red-50';
    if (score >= 85) return 'text-yellow-600 bg-yellow-50';
    return 'text-green-600 bg-green-50';
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Buscar PEP</h1>
        <p className="text-gray-500">Consulta en la base de datos de funcionarios publicos de Panama</p>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="card">
            <p className="text-sm text-gray-500">Total Funcionarios</p>
            <p className="text-2xl font-bold text-gray-900">{stats.total_funcionarios.toLocaleString()}</p>
          </div>
          <div className="card">
            <p className="text-sm text-gray-500">Clasificados como PEP</p>
            <p className="text-2xl font-bold text-red-600">{stats.clasificados_pep.toLocaleString()}</p>
          </div>
          <div className="card">
            <p className="text-sm text-gray-500">Fuente</p>
            <p className="text-sm text-gray-700">datosabiertos.gob.pa</p>
          </div>
        </div>
      )}

      {/* Search Form */}
      <div className="card">
        <h2 className="font-semibold mb-4 flex items-center">
          <Search className="w-5 h-5 mr-2 text-primary-600" />
          Buscar por Datos Personales
        </h2>
        
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="label">Nombre</label>
              <input
                type="text"
                value={nombre}
                onChange={(e) => setNombre(e.target.value)}
                className="input"
                placeholder="Ingrese nombre"
              />
            </div>
            <div>
              <label className="label">Apellido</label>
              <input
                type="text"
                value={apellido}
                onChange={(e) => setApellido(e.target.value)}
                className="input"
                placeholder="Ingrese apellido"
              />
            </div>
            <div>
              <label className="label">Cedula</label>
              <input
                type="text"
                value={cedula}
                onChange={(e) => setCedula(e.target.value)}
                className="input"
                placeholder="Ej: 8-123-456"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || (!nombre && !apellido && !cedula)}
            className="btn-primary flex items-center"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Buscando...
              </>
            ) : (
              <>
                <Search className="w-5 h-5 mr-2" />
                Buscar
              </>
            )}
          </button>
        </form>
      </div>

      {/* Results */}
      {buscado && (
        <div className="card">
          <h2 className="font-semibold mb-4">
            Resultados ({resultados.length})
          </h2>

          {loading ? (
            <div className="flex items-center justify-center h-32">
              <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
            </div>
          ) : resultados.length === 0 ? (
            <div className="text-center py-8">
              <CheckCircle className="w-12 h-12 text-green-400 mx-auto mb-3" />
              <p className="text-gray-500">No se encontraron coincidencias</p>
              <p className="text-sm text-gray-400 mt-1">
                La persona no aparece en la base de datos de funcionarios publicos
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {resultados.map((resultado, index) => (
                <div
                  key={index}
                  className={clsx(
                    'p-4 rounded-lg border-2',
                    resultado.es_exacto 
                      ? 'border-red-300 bg-red-50' 
                      : resultado.score_similitud >= 85 
                        ? 'border-yellow-300 bg-yellow-50'
                        : 'border-gray-200 bg-white'
                  )}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      <div className={clsx(
                        'p-2 rounded-full',
                        resultado.es_exacto ? 'bg-red-100' : 'bg-gray-100'
                      )}>
                        {resultado.es_exacto ? (
                          <AlertTriangle className="w-5 h-5 text-red-600" />
                        ) : (
                          <User className="w-5 h-5 text-gray-600" />
                        )}
                      </div>
                      <div>
                        <p className="font-semibold">
                          {resultado.nombre} {resultado.apellido}
                        </p>
                        {resultado.cedula && (
                          <p className="text-sm text-gray-500">Cedula: {resultado.cedula}</p>
                        )}
                        {resultado.cargo_designacion && (
                          <p className="text-sm mt-1">
                            <Building className="w-4 h-4 inline mr-1 text-gray-400" />
                            {resultado.cargo_designacion}
                          </p>
                        )}
                        {resultado.institucion && (
                          <p className="text-sm text-gray-500">{resultado.institucion}</p>
                        )}
                      </div>
                    </div>

                    <div className="text-right">
                      <span className={clsx(
                        'px-3 py-1 rounded-full text-sm font-medium',
                        getScoreColor(resultado.score_similitud)
                      )}>
                        {resultado.score_similitud.toFixed(0)}%
                      </span>
                      {resultado.es_exacto && (
                        <p className="text-xs text-red-600 mt-1 font-medium">Coincidencia EXACTA</p>
                      )}
                    </div>
                  </div>
                </div>
              ))}

              <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm text-blue-800">
                  <strong>Nota:</strong> Los resultados se basan en coincidencias de nombres y cedulas
                  en la base de datos de funcionarios publicos de Panama. Una coincidencia no confirma
                  automaticamente que la persona sea una PEP, pero indica que requiere verificacion adicional.
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Listado de Cargos PEP */}
      <div className="card">
        <button
          onClick={() => setShowCargos(!showCargos)}
          className="w-full flex items-center justify-between"
        >
          <h2 className="font-semibold flex items-center">
            <Scale className="w-5 h-5 mr-2 text-primary-600" />
            Cargos Considerados PEP segun la Ley de Panama
          </h2>
          {showCargos ? (
            <ChevronUp className="w-5 h-5 text-gray-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-400" />
          )}
        </button>

        {showCargos && (
          <div className="mt-4 space-y-4">
            {cargosPEP.map((cat) => (
              <div key={cat.categoria}>
                <h4 className="font-medium text-sm text-primary-700 mb-2">{cat.categoria}</h4>
                <ul className="space-y-1">
                  {cat.cargos.map((cargo) => (
                    <li key={cargo} className="flex items-center text-sm text-gray-600">
                      <span className="w-1.5 h-1.5 bg-primary-400 rounded-full mr-2 flex-shrink-0" />
                      {cargo}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Info Box */}
      <div className="card bg-gray-50">
        <h3 className="font-semibold mb-2">Acerca de la Busqueda PEP</h3>
        <p className="text-sm text-gray-600 mb-2">
          Esta busqueda consulta la base de datos de Designacion de Funcionarios de Altos Mandos
          publicada por la Superintendencia de Bancos de Panama en datosabiertos.gob.pa.
        </p>
        <ul className="text-sm text-gray-600 list-disc list-inside space-y-1">
          <li>Cedula exacta = Coincidencia 100% (ALERTA ALTA)</li>
          <li>Nombre + Apellido con similitud &gt;= 85% = Coincidencia probable (ALERTA MEDIA)</li>
          <li>Similitud &lt; 85% = Sin coincidencia significativa</li>
        </ul>
      </div>
    </div>
  );
}
