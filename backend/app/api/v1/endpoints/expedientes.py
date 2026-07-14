from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.models import Expediente, Cliente, EventoAuditoria, EstadoExpediente
from app.schemas.schemas import ExpedienteCreate, ExpedienteUpdate, ExpedienteResponse, ExpedienteDetalleResponse
from app.services.pdf_service import generar_pdf_expediente
import uuid

router = APIRouter()


def generar_numero_expediente() -> str:
    fecha = datetime.now().strftime("%Y%m%d")
    uid = uuid.uuid4().hex[:8].upper()
    return f"EDD-{fecha}-{uid}"


@router.get("/", response_model=List[ExpedienteResponse])
def listar_expedientes(
    skip: int = 0,
    limit: int = 100,
    estado: str = None,
    nivel_riesgo: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(Expediente)

    if estado:
        query = query.filter(Expediente.estado == estado)
    if nivel_riesgo:
        query = query.filter(Expediente.nivel_riesgo == nivel_riesgo)

    expedientes = query.offset(skip).limit(limit).all()
    return expedientes


@router.get("/{expediente_id}", response_model=ExpedienteDetalleResponse)
def obtener_expediente(
    expediente_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    expediente = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    if not expediente:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")
    return expediente


@router.get("/{expediente_id}/pdf")
def exportar_expediente_pdf(
    expediente_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    expediente = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    if not expediente:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")

    pdf_bytes = generar_pdf_expediente(
        expediente=expediente,
        cliente=expediente.cliente,
        documentos=expediente.documentos,
        eventos=expediente.eventos,
    )

    db.add(EventoAuditoria(
        expediente_id=expediente.id,
        usuario=current_user.get("user_id", "system"),
        accion="EXPORTAR_PDF",
        detalles={"numero_expediente": expediente.numero_expediente}
    ))
    db.commit()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{expediente.numero_expediente}.pdf"'
        }
    )


@router.post("/", response_model=ExpedienteResponse, status_code=status.HTTP_201_CREATED)
def crear_expediente(
    expediente: ExpedienteCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cliente = db.query(Cliente).filter(Cliente.id == expediente.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    numero = generar_numero_expediente()

    db_expediente = Expediente(
        numero_expediente=numero,
        **expediente.model_dump()
    )
    db.add(db_expediente)
    db.commit()
    db.refresh(db_expediente)

    evento = EventoAuditoria(
        expediente_id=db_expediente.id,
        usuario=current_user.get("user_id", "system"),
        accion="CREAR_EXPEDIENTE",
        detalles={"numero": numero}
    )
    db.add(evento)
    db.commit()

    return db_expediente


@router.put("/{expediente_id}", response_model=ExpedienteResponse)
def actualizar_expediente(
    expediente_id: int,
    expediente_update: ExpedienteUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    expediente = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    if not expediente:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")

    update_data = expediente_update.model_dump(exclude_unset=True)

    if "estado" in update_data and update_data["estado"] != expediente.estado:
        evento = EventoAuditoria(
            expediente_id=expediente.id,
            usuario=current_user.get("user_id", "system"),
            accion=f"CAMBIO_ESTADO:{update_data['estado']}",
            detalles={"estado_anterior": expediente.estado}
        )
        db.add(evento)

    for field, value in update_data.items():
        setattr(expediente, field, value)

    expediente.version += 1
    db.commit()
    db.refresh(expediente)
    return expediente


@router.post("/{expediente_id}/aprobar", response_model=ExpedienteResponse)
def aprobar_expediente(
    expediente_id: int,
    comentario: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("alta_gerencia"))
):
    expediente = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    if not expediente:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")

    if expediente.estado != EstadoExpediente.PENDIENTE_GERENCIA:
        raise HTTPException(
            status_code=400,
            detail=f"El expediente debe estar en estado pendiente_gerencia para aprobar. Estado actual: {expediente.estado.value}"
        )

    if not comentario:
        raise HTTPException(status_code=400, detail="Comentario obligatorio para aprobación")

    expediente.estado = EstadoExpediente.APROBADO
    expediente.aprobado_por = current_user.get("user_id")
    expediente.fecha_aprobacion = datetime.utcnow()
    expediente.comentario_aprobacion = comentario

    evento = EventoAuditoria(
        expediente_id=expediente.id,
        usuario=current_user.get("user_id"),
        accion="APROBAR",
        detalles={"comentario": comentario}
    )
    db.add(evento)

    db.commit()
    db.refresh(expediente)

    return expediente


@router.post("/{expediente_id}/rechazar", response_model=ExpedienteResponse)
def rechazar_expediente(
    expediente_id: int,
    comentario: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("alta_gerencia"))
):
    if not comentario:
        raise HTTPException(status_code=400, detail="Comentario obligatorio para rechazo")

    expediente = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    if not expediente:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")

    expediente.estado = EstadoExpediente.RECHAZADO
    expediente.comentario_aprobacion = comentario

    evento = EventoAuditoria(
        expediente_id=expediente.id,
        usuario=current_user.get("user_id"),
        accion="RECHAZAR",
        detalles={"comentario": comentario}
    )
    db.add(evento)

    db.commit()
    db.refresh(expediente)
    return expediente
