import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { expedienteService } from '../services/expedienteService';
import { documentoService } from '../services/documentoService';
import type { ExpedienteDetalle, Documento, EventoAuditoria, NivelRiesgo } from '../types';
import toast from 'react-hot-toast';
import {
  ArrowLeft,
  FileText,
  Upload,
  Clock,
  CheckCircle,
  XCircle,
  Shield,
  Download,
} from 'lucide-react';
import clsx from 'clsx';

const RIESGO_COLORS: Record<NivelRiesgo, string> = {
  bajo: 'bg-green-100 text-green-700',
  medio: 'bg-yellow-100 text-yellow-700',
  alto: 'bg-red-100 text-red-700',
};

export default function ExpedienteDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [expediente, setExpediente] = useState<ExpedienteDetalle | null>(null);
  const [documentos, setDocumentos] = useState<Documento[]>([]);
  const [eventos, setEventos] = useState<EventoAuditoria[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [activeTab, setActiveTab] = useState<'detalle' | 'documentos' | 'trazabilidad'>('detalle');

  useEffect(() => {
    if (id) {
      fetchExpediente();
    }
  }, [id]);

  const fetchExpediente = async () => {
    try {
      const data = await expedienteService.get(Number(id));
      setExpediente(data);
      setDocumentos(data.documentos || []);
      setEventos(data.eventos || []);
    } catch (err) {
      toast.error('Error al cargar expediente');
      navigate('/expedientes');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const doc = await documentoService.upload(
          Number(id),
          file.name.split('.').pop() || 'otro',
          file
        );
        setDocumentos((prev) => [...prev, doc]);
      }
      toast.success('Documento(s) subido(s) exitosamente');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al subir documento');
    } finally {
      setUploading(false);
    }
  };

  const handleExportarPdf = async () => {
    if (!expediente) return;
    setExporting(true);
    try {
      await expedienteService.exportarPdf(Number(id), expediente.numero_expediente);
      toast.success('PDF exportado');
    } catch (err) {
      toast.error('Error al exportar PDF');
    } finally {
      setExporting(false);
    }
  };

  const handleAprobar = async () => {
    const comentario = prompt('Ingrese un comentario de aprobacion (obligatorio):');
    if (!comentario) return;

    try {
      await expedienteService.aprobar(Number(id), comentario);
      toast.success('Expediente aprobado');
      fetchExpediente();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al aprobar');
    }
  };

  const handleRechazar = async () => {
    const comentario = prompt('Ingrese el motivo del rechazo (obligatorio):');
    if (!comentario) return;

    try {
      await expedienteService.rechazar(Number(id), comentario);
      toast.success('Expediente rechazado');
      fetchExpediente();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al rechazar');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!expediente) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/expedientes')}
            aria-label="Volver a expedientes"
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{expediente.numero_expediente}</h1>
            <p className="text-gray-500">
              Cliente: {expediente.cliente.nombre} {expediente.cliente.apellido}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <span className={clsx('px-3 py-1 rounded-full text-sm font-medium capitalize', RIESGO_COLORS[expediente.nivel_riesgo])}>
            {expediente.nivel_riesgo}
          </span>
          {expediente.score_riesgo !== null && expediente.score_riesgo !== undefined && (
            <span className="text-sm text-gray-500">
              Score: {expediente.score_riesgo.toFixed(0)}
            </span>
          )}
          <button
            onClick={handleExportarPdf}
            disabled={exporting}
            className="btn-primary flex items-center"
            aria-label="Exportar expediente a PDF"
          >
            <Download className="w-5 h-5 mr-2" />
            {exporting ? 'Exportando...' : 'Exportar PDF'}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b">
        <nav className="flex space-x-8">
          {[
            { id: 'detalle', label: 'Detalle' },
            { id: 'documentos', label: `Documentos (${documentos.length})` },
            { id: 'trazabilidad', label: 'Trazabilidad' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={clsx(
                'py-4 px-1 border-b-2 text-sm font-medium',
                activeTab === tab.id
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              )}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      {activeTab === 'detalle' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Info Cliente */}
          <div className="card">
            <h3 className="font-semibold mb-4 flex items-center">
              <Shield className="w-5 h-5 mr-2 text-primary-600" />
              Informacion del Cliente
            </h3>
            <dl className="space-y-3 text-sm">
              <div className="flex justify-between">
                <dt className="text-gray-500">Tipo:</dt>
                <dd className="font-medium">{expediente.cliente.tipo_persona}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Identificacion:</dt>
                <dd className="font-medium">{expediente.cliente.numero_identificacion}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Nacionalidad:</dt>
                <dd className="font-medium">{expediente.cliente.nacionalidad || 'N/A'}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Pais Residencia:</dt>
                <dd className="font-medium">{expediente.cliente.pais_residencia || 'N/A'}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">PEP:</dt>
                <dd className="font-medium">
                  {expediente.cliente.es_pep ? (
                    <span className="text-red-600">Si ({expediente.cliente.cargo_pep})</span>
                  ) : (
                    <span className="text-green-600">No</span>
                  )}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Ingresos Anuales:</dt>
                <dd className="font-medium">
                  {expediente.cliente.ingresos_anuales 
                    ? `$${expediente.cliente.ingresos_anuales.toLocaleString()}`
                    : 'N/A'}
                </dd>
              </div>
            </dl>
          </div>

          {/* Info Expediente */}
          <div className="card">
            <h3 className="font-semibold mb-4">Estado del Expediente</h3>
            <dl className="space-y-3 text-sm">
              <div className="flex justify-between">
                <dt className="text-gray-500">Estado:</dt>
                <dd className="font-medium capitalize">{expediente.estado.replace('_', ' ')}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Version:</dt>
                <dd className="font-medium">{expediente.version}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Creado:</dt>
                <dd className="font-medium">
                  {new Date(expediente.created_at).toLocaleString('es-PA')}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Ultima Actualizacion:</dt>
                <dd className="font-medium">
                  {new Date(expediente.updated_at).toLocaleString('es-PA')}
                </dd>
              </div>
              {expediente.aprobado_por && (
                <div className="flex justify-between">
                  <dt className="text-gray-500">Aprobado por:</dt>
                  <dd className="font-medium">{expediente.aprobado_por}</dd>
                </div>
              )}
            </dl>

            {/* Actions */}
            <div className="mt-6 pt-4 border-t space-y-3">
              {expediente.estado === 'pendiente_gerencia' && (
                <>
                  <button
                    onClick={handleAprobar}
                    className="btn-primary w-full flex items-center justify-center"
                  >
                    <CheckCircle className="w-5 h-5 mr-2" />
                    Aprobar
                  </button>
                  <button
                    onClick={handleRechazar}
                    className="btn-danger w-full flex items-center justify-center"
                  >
                    <XCircle className="w-5 h-5 mr-2" />
                    Rechazar
                  </button>
                </>
              )}
              {expediente.estado === 'borrador' && (
                <button
                  onClick={async () => {
                    try {
                      await expedienteService.update(Number(id), { estado: 'pendiente_revision' });
                      toast.success('Expediente enviado a revisión');
                      fetchExpediente();
                    } catch (err: any) {
                      toast.error(err.response?.data?.detail || 'Error al enviar a revisión');
                    }
                  }}
                  className="btn-primary w-full flex items-center justify-center"
                >
                  <CheckCircle className="w-5 h-5 mr-2" />
                  Enviar para Revision
                </button>
              )}
              {expediente.estado === 'pendiente_revision' && (
                <button
                  onClick={async () => {
                    try {
                      await expedienteService.update(Number(id), { estado: 'pendiente_gerencia' });
                      toast.success('Expediente enviado a gerencia');
                      fetchExpediente();
                    } catch (err: any) {
                      toast.error(err.response?.data?.detail || 'Error al enviar a gerencia');
                    }
                  }}
                  className="btn-primary w-full flex items-center justify-center"
                >
                  <CheckCircle className="w-5 h-5 mr-2" />
                  Enviar a Gerencia
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'documentos' && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Documentos Adjuntos</h3>
            <label className="btn-primary cursor-pointer flex items-center">
              <Upload className="w-5 h-5 mr-2" />
              {uploading ? 'Subiendo...' : 'Subir Documento'}
              <input
                type="file"
                multiple
                accept=".pdf,.png,.jpg,.jpeg"
                onChange={handleFileUpload}
                className="hidden"
                disabled={uploading}
              />
            </label>
          </div>

          {documentos.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              <FileText className="w-12 h-12 mx-auto mb-3" />
              <p>No hay documentos adjuntos</p>
            </div>
          ) : (
            <div className="space-y-3">
              {documentos.map((doc) => (
                <div key={doc.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <FileText className="w-5 h-5 text-gray-400" />
                    <div>
                      <p className="font-medium text-sm">{doc.nombre_archivo}</p>
                      <p className="text-xs text-gray-500">
                        {(doc.tamano_bytes / 1024).toFixed(1)} KB - {doc.tipo_documento}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-gray-400">
                      {new Date(doc.uploaded_at).toLocaleDateString('es-PA')}
                    </span>
                    <button
                      onClick={() => documentoService.download(
                        Number(id), doc.id, doc.nombre_archivo
                      )}
                      aria-label="Descargar documento"
                      className="p-1 hover:bg-gray-200 rounded"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'trazabilidad' && (
        <div className="card">
          <h3 className="font-semibold mb-4">Historial de Eventos</h3>
          {eventos.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              <Clock className="w-12 h-12 mx-auto mb-3" />
              <p>No hay eventos registrados</p>
            </div>
          ) : (
            <div className="space-y-4">
              {eventos.map((evento) => (
                <div key={evento.id} className="flex items-start space-x-3">
                  <div className="p-2 bg-gray-100 rounded-full">
                    <Clock className="w-4 h-4 text-gray-500" />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-sm">{evento.accion}</p>
                    <p className="text-xs text-gray-500">
                      {evento.usuario} - {new Date(evento.created_at).toLocaleString('es-PA')}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
