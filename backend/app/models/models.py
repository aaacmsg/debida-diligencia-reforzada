from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, Enum, ForeignKey, JSON, event
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class TipoPersona(str, enum.Enum):
    NATURAL = "natural"
    JURIDICA = "juridica"


class TipoIdentificacion(str, enum.Enum):
    CEDULA = "cedula"
    PASAPORTE = "pasaporte"
    RUC = "ruc"


class NivelRiesgo(str, enum.Enum):
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"


class EstadoExpediente(str, enum.Enum):
    BORRADOR = "borrador"
    PENDIENTE_INFO = "pendiente_info"
    PENDIENTE_REVISION = "pendiente_revision"
    PENDIENTE_GERENCIA = "pendiente_gerencia"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    tipo_persona = Column(Enum(TipoPersona), nullable=False)
    nombre = Column(String(255), nullable=False)
    apellido = Column(String(255), nullable=True)
    razon_social = Column(String(255), nullable=True)
    tipo_identificacion = Column(Enum(TipoIdentificacion), nullable=False)
    numero_identificacion = Column(String(50), nullable=False, unique=True, index=True)
    fecha_nacimiento = Column(DateTime, nullable=True)
    nacionalidad = Column(String(100), nullable=True)
    pais_residencia = Column(String(100), nullable=True)
    direccion = Column(Text, nullable=True)
    telefono = Column(String(50), nullable=True)
    correo = Column(String(255), nullable=True)

    es_pep = Column(Boolean, default=False)
    cargo_pep = Column(String(255), nullable=True)
    relacion_pep = Column(String(255), nullable=True)
    pais_residencia_fiscal = Column(String(100), nullable=True)

    actividad_economica = Column(String(255), nullable=True)
    sector_economico = Column(String(100), nullable=True)
    ingresos_anuales = Column(Float, nullable=True)
    patrimonio = Column(Float, nullable=True)
    origen_fondos = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(100), nullable=True)

    expedientes = relationship("Expediente", back_populates="cliente")
    beneficiarios_finales = relationship("BeneficiarioFinal", back_populates="cliente")


class BeneficiarioFinal(Base):
    __tablename__ = "beneficiarios_finales"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    nombre = Column(String(255), nullable=False)
    apellido = Column(String(255), nullable=True)
    numero_identificacion = Column(String(50), nullable=False)
    porcentaje_participacion = Column(Float, nullable=False)
    tipo_control = Column(String(100), nullable=True)
    pais_residencia = Column(String(100), nullable=True)
    es_pep = Column(Boolean, default=False)

    created_at = Column(DateTime, server_default=func.now())

    cliente = relationship("Cliente", back_populates="beneficiarios_finales")


class Expediente(Base):
    __tablename__ = "expedientes"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    numero_expediente = Column(String(50), unique=True, nullable=False, index=True)

    nivel_riesgo = Column(Enum(NivelRiesgo), default=NivelRiesgo.BAJO)
    score_riesgo = Column(Float, nullable=True)
    variables_riesgo = Column(JSON, nullable=True)

    estado = Column(Enum(EstadoExpediente), default=EstadoExpediente.BORRADOR)

    requiere_aprobacion_gerencial = Column(Boolean, default=False)
    aprobado_por = Column(String(100), nullable=True)
    fecha_aprobacion = Column(DateTime, nullable=True)
    comentario_aprobacion = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(100), nullable=True)
    version = Column(Integer, default=1)

    cliente = relationship("Cliente", back_populates="expedientes")
    documentos = relationship("Documento", back_populates="expediente")
    eventos = relationship("EventoAuditoria", back_populates="expediente")
    alertas = relationship("Alerta", back_populates="expediente")


class Documento(Base):
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True, index=True)
    expediente_id = Column(Integer, ForeignKey("expedientes.id"), nullable=False)
    tipo_documento = Column(String(100), nullable=False)
    nombre_archivo = Column(String(255), nullable=False)
    ruta_archivo = Column(String(500), nullable=False)
    hash_sha256 = Column(String(64), nullable=False)
    tamano_bytes = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=True)

    uploaded_at = Column(DateTime, server_default=func.now())
    uploaded_by = Column(String(100), nullable=True)
    malware_scan_result = Column(String(50), nullable=True)

    expediente = relationship("Expediente", back_populates="documentos")


class FuncionarioPublico(Base):
    __tablename__ = "funcionarios_publicos"

    id = Column(Integer, primary_key=True, index=True)
    cedula = Column(String(50), nullable=False, index=True)
    nombre = Column(String(255), nullable=False)
    apellido = Column(String(255), nullable=False)
    cargo_permanente = Column(String(255), nullable=True)
    cargo_designacion = Column(String(255), nullable=False)
    institucion = Column(String(255), nullable=False)
    fecha_inicio = Column(DateTime, nullable=True)
    fecha_final = Column(DateTime, nullable=True)
    numero_resolucion = Column(String(100), nullable=True)

    es_pep = Column(Boolean, default=False)
    nivel_cargo = Column(String(50), nullable=True)

    downloaded_at = Column(DateTime, server_default=func.now())
    source = Column(String(100), nullable=True)


class EventoAuditoria(Base):
    __tablename__ = "eventos_auditoria"

    id = Column(Integer, primary_key=True, index=True)
    expediente_id = Column(Integer, ForeignKey("expedientes.id"), nullable=True)
    usuario = Column(String(100), nullable=False)
    accion = Column(String(100), nullable=False)
    detalles = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)

    expediente = relationship("Expediente", back_populates="eventos")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    rol = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Configuracion(Base):
    __tablename__ = "configuracion"

    id = Column(Integer, primary_key=True, index=True)
    clave = Column(String(100), unique=True, nullable=False, index=True)
    valor = Column(String(500), nullable=False)
    descripcion = Column(String(500), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    updated_by = Column(String(100), nullable=True)


class Alerta(Base):
    __tablename__ = "alertas"

    id = Column(Integer, primary_key=True, index=True)
    expediente_id = Column(Integer, ForeignKey("expedientes.id"), nullable=True)
    tipo_alerta = Column(String(100), nullable=False)
    mensaje = Column(Text, nullable=False)
    nivel = Column(String(20), nullable=False)
    leida = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(100), nullable=True)

    created_at = Column(DateTime, server_default=func.now(), index=True)

    expediente = relationship("Expediente", back_populates="alertas")


class AuditoriaInmutableError(Exception):
    """Los eventos de auditoria son WORM (Ley 23 Art. 21): solo escritura, nunca edicion/borrado."""


@event.listens_for(EventoAuditoria, "before_update")
def _bloquear_update_auditoria(mapper, connection, target):
    raise AuditoriaInmutableError(
        f"Evento de auditoria {target.id} es inmutable (WORM): no se permite modificar"
    )


@event.listens_for(EventoAuditoria, "before_delete")
def _bloquear_delete_auditoria(mapper, connection, target):
    raise AuditoriaInmutableError(
        f"Evento de auditoria {target.id} es inmutable (WORM): no se permite eliminar"
    )