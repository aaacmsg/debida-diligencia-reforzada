export type TipoPersona = 'natural' | 'juridica';
export type TipoIdentificacion = 'cedula' | 'pasaporte' | 'ruc';
export type NivelRiesgo = 'bajo' | 'medio' | 'alto';
export type EstadoExpediente = 
  | 'borrador' 
  | 'pendiente_info' 
  | 'pendiente_revision' 
  | 'pendiente_gerencia' 
  | 'aprobado' 
  | 'rechazado';

export interface Cliente {
  id: number;
  tipo_persona: TipoPersona;
  nombre: string;
  apellido?: string;
  razon_social?: string;
  tipo_identificacion: TipoIdentificacion;
  numero_identificacion: string;
  fecha_nacimiento?: string;
  nacionalidad?: string;
  pais_residencia?: string;
  direccion?: string;
  telefono?: string;
  correo?: string;
  es_pep: boolean;
  cargo_pep?: string;
  relacion_pep?: string;
  pais_residencia_fiscal?: string;
  actividad_economica?: string;
  sector_economico?: string;
  ingresos_anuales?: number;
  patrimonio?: number;
  origen_fondos?: string;
  created_at: string;
  updated_at: string;
}

export interface BeneficiarioFinal {
  id: number;
  cliente_id: number;
  nombre: string;
  apellido?: string;
  numero_identificacion: string;
  porcentaje_participacion: number;
  tipo_control?: string;
  pais_residencia?: string;
  es_pep: boolean;
  created_at: string;
}

export interface BeneficiarioFinalCreate {
  nombre: string;
  apellido?: string;
  numero_identificacion: string;
  porcentaje_participacion: number;
  tipo_control?: string;
  pais_residencia?: string;
  es_pep: boolean;
}

export interface Expediente {
  id: number;
  cliente_id: number;
  numero_expediente: string;
  nivel_riesgo: NivelRiesgo;
  score_riesgo?: number;
  variables_riesgo?: Record<string, unknown>;
  estado: EstadoExpediente;
  requiere_aprobacion_gerencial: boolean;
  aprobado_por?: string;
  fecha_aprobacion?: string;
  comentario_aprobacion?: string;
  created_at: string;
  updated_at: string;
  version: number;
}

export interface ExpedienteDetalle extends Expediente {
  cliente: Cliente;
  documentos: Documento[];
  eventos: EventoAuditoria[];
}

export interface Documento {
  id: number;
  expediente_id: number;
  tipo_documento: string;
  nombre_archivo: string;
  ruta_archivo: string;
  hash_sha256: string;
  tamano_bytes: number;
  mime_type?: string;
  uploaded_at: string;
  uploaded_by?: string;
  malware_scan_result?: string;
}

export interface FuncionarioPublico {
  id: number;
  cedula: string;
  nombre: string;
  apellido: string;
  cargo_permanente?: string;
  cargo_designacion: string;
  institucion: string;
  fecha_inicio?: string;
  fecha_final?: string;
  numero_resolucion?: string;
  es_pep: boolean;
  nivel_cargo?: string;
  downloaded_at: string;
  source?: string;
}

export interface PEPSearchResult {
  cedula?: string;
  nombre: string;
  apellido: string;
  cargo_designacion?: string;
  institucion?: string;
  score_similitud: number;
  es_exacto: boolean;
}

export interface EventoAuditoria {
  id: number;
  expediente_id?: number;
  usuario: string;
  accion: string;
  detalles?: Record<string, unknown>;
  ip_address?: string;
  created_at: string;
}

export interface CalculoRiesgoRequest {
  pais_residencia?: string;
  pais_nacimiento?: string;
  pais_residencia_fiscal?: string;
  es_pep: boolean;
  cargo_pep?: string;
  sector_economico?: string;
  actividad_economica?: string;
  vinculos_pep: number;
  origen_fondos_documentado: boolean;
}

export interface CalculoRiesgoResponse {
  score_total: number;
  nivel_riesgo: NivelRiesgo;
  variables: {
    pais: { score: number; detalle: Record<string, unknown> };
    cargo: { score: number; detalle: Record<string, unknown> };
    sector: { score: number; detalle: Record<string, unknown> };
    vinculos: { score: number; detalle: Record<string, unknown> };
    origen_fondos: { score: number; detalle: Record<string, unknown> };
  };
  ponderacion: Record<string, number>;
}

export interface Usuario {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  rol: string;
  is_active: boolean;
  created_at: string;
}

export interface Alerta {
  id: number;
  expediente_id?: number;
  tipo_alerta: string;
  mensaje: string;
  nivel: 'bajo' | 'medio' | 'alto';
  leida: boolean;
  resolved_at?: string;
  resolved_by?: string;
  created_at: string;
}

export interface DashboardStats {
  total_expedientes: number;
  por_estado: Record<string, number>;
  por_riesgo: Record<string, number>;
}

export interface GraphNode {
  id: string;
  label: string;
  type: 'cliente' | 'empresa' | 'persona' | 'documento';
  riesgo?: NivelRiesgo;
  es_pep?: boolean;
}

export interface GraphEdge {
  source: string;
  target: string;
  label?: string;
  type: 'accionista' | 'representante' | 'vinculo' | 'documento';
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}
