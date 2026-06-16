from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TipoPersona(str, Enum):
    NATURAL = "natural"
    JURIDICA = "juridica"


class TipoIdentificacion(str, Enum):
    CEDULA = "cedula"
    PASAPORTE = "pasaporte"
    RUC = "ruc"


class NivelRiesgo(str, Enum):
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"


class EstadoExpediente(str, Enum):
    BORRADOR = "borrador"
    PENDIENTE_INFO = "pendiente_info"
    PENDIENTE_REVISION = "pendiente_revision"
    PENDIENTE_GERENCIA = "pendiente_gerencia"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"


# Cliente Schemas
class ClienteBase(BaseModel):
    tipo_persona: TipoPersona
    nombre: str = Field(..., min_length=1, max_length=255)
    apellido: Optional[str] = None
    razon_social: Optional[str] = None
    tipo_identificacion: TipoIdentificacion
    numero_identificacion: str = Field(..., min_length=1, max_length=50)
    fecha_nacimiento: Optional[datetime] = None
    nacionalidad: Optional[str] = None
    pais_residencia: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None
    es_pep: bool = False
    cargo_pep: Optional[str] = None
    relacion_pep: Optional[str] = None
    pais_residencia_fiscal: Optional[str] = None
    actividad_economica: Optional[str] = None
    sector_economico: Optional[str] = None
    ingresos_anuales: Optional[float] = None
    patrimonio: Optional[float] = None
    origen_fondos: Optional[str] = None


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    tipo_persona: Optional[TipoPersona] = None
    nombre: Optional[str] = Field(None, min_length=1, max_length=255)
    apellido: Optional[str] = None
    razon_social: Optional[str] = None
    tipo_identificacion: Optional[TipoIdentificacion] = None
    numero_identificacion: Optional[str] = Field(None, min_length=1, max_length=50)
    fecha_nacimiento: Optional[datetime] = None
    nacionalidad: Optional[str] = None
    pais_residencia: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None
    es_pep: Optional[bool] = None
    cargo_pep: Optional[str] = None
    relacion_pep: Optional[str] = None
    pais_residencia_fiscal: Optional[str] = None
    actividad_economica: Optional[str] = None
    sector_economico: Optional[str] = None
    ingresos_anuales: Optional[float] = None
    patrimonio: Optional[float] = None
    origen_fondos: Optional[str] = None


class ClienteResponse(ClienteBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Beneficiario Final Schemas
class BeneficiarioFinalBase(BaseModel):
    nombre: str
    apellido: Optional[str] = None
    numero_identificacion: str
    porcentaje_participacion: float = Field(..., ge=0, le=100)
    tipo_control: Optional[str] = None
    pais_residencia: Optional[str] = None
    es_pep: bool = False


class BeneficiarioFinalCreate(BeneficiarioFinalBase):
    cliente_id: int


class BeneficiarioFinalResponse(BeneficiarioFinalBase):
    id: int
    cliente_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Expediente Schemas
class ExpedienteBase(BaseModel):
    cliente_id: int
    nivel_riesgo: NivelRiesgo = NivelRiesgo.BAJO
    score_riesgo: Optional[float] = None
    variables_riesgo: Optional[dict] = None


class ExpedienteCreate(ExpedienteBase):
    pass


class ExpedienteUpdate(BaseModel):
    nivel_riesgo: Optional[NivelRiesgo] = None
    score_riesgo: Optional[float] = None
    variables_riesgo: Optional[dict] = None
    estado: Optional[EstadoExpediente] = None
    comentario_aprobacion: Optional[str] = None


class ExpedienteResponse(ExpedienteBase):
    id: int
    numero_expediente: str
    estado: EstadoExpediente
    requiere_aprobacion_gerencial: bool
    aprobado_por: Optional[str] = None
    fecha_aprobacion: Optional[datetime] = None
    comentario_aprobacion: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True


class ExpedienteDetalleResponse(ExpedienteResponse):
    cliente: ClienteResponse
    documentos: List["DocumentoResponse"] = []
    eventos: List["EventoAuditoriaResponse"] = []


# Documento Schemas
class DocumentoBase(BaseModel):
    tipo_documento: str
    nombre_archivo: str
    ruta_archivo: str
    hash_sha256: str
    tamano_bytes: int
    mime_type: Optional[str] = None


class DocumentoResponse(DocumentoBase):
    id: int
    expediente_id: int
    uploaded_at: datetime
    uploaded_by: Optional[str] = None
    malware_scan_result: Optional[str] = None

    class Config:
        from_attributes = True


# Riesgo Schemas
class CalculoRiesgoRequest(BaseModel):
    pais_residencia: Optional[str] = None
    pais_nacimiento: Optional[str] = None
    pais_residencia_fiscal: Optional[str] = None
    es_pep: bool = False
    cargo_pep: Optional[str] = None
    sector_economico: Optional[str] = None
    actividad_economica: Optional[str] = None
    vinculos_pep: int = 0
    origen_fondos_documentado: bool = True


class CalculoRiesgoResponse(BaseModel):
    score_total: float
    nivel_riesgo: NivelRiesgo
    variables: dict
    ponderacion: dict


# PEP Search Schemas
class PEPSearchRequest(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    cedula: Optional[str] = None


class PEPSearchResponse(BaseModel):
    cedula: Optional[str] = None
    nombre: str
    apellido: str
    cargo_designacion: Optional[str] = None
    institucion: Optional[str] = None
    score_similitud: float
    es_exacto: bool


# Auditoria Schemas
class EventoAuditoriaResponse(BaseModel):
    id: int
    expediente_id: Optional[int] = None
    usuario: str
    accion: str
    detalles: Optional[dict] = None
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    roles: List[str] = []


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    rol: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Alerta Schemas
class AlertaResponse(BaseModel):
    id: int
    expediente_id: Optional[int] = None
    tipo_alerta: str
    mensaje: str
    nivel: str
    leida: bool
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
