from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Cliente, Expediente, EventoAuditoria
from app.schemas.schemas import ClienteCreate, ClienteUpdate, ClienteResponse, ExpedienteResponse, CalculoRiesgoRequest, NivelRiesgo
from app.services.riesgo_service import riesgo_service

router = APIRouter()


def generar_numero_expediente() -> str:
    fecha = datetime.now().strftime("%Y%m%d")
    uid = uuid.uuid4().hex[:8].upper()
    return f"EDD-{fecha}-{uid}"


@router.get("/", response_model=List[ClienteResponse])
def listar_clientes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    clientes = db.query(Cliente).offset(skip).limit(limit).all()
    return clientes


@router.get("/{cliente_id}", response_model=ClienteResponse)
def obtener_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def crear_cliente(
    cliente: ClienteCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    existente = db.query(Cliente).filter(
        Cliente.numero_identificacion == cliente.numero_identificacion
    ).first()

    if existente:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un cliente con esta identificación"
        )

    db_cliente = Cliente(**cliente.model_dump())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)

    riesgo_request = CalculoRiesgoRequest(
        pais_residencia=cliente.pais_residencia,
        pais_residencia_fiscal=cliente.pais_residencia_fiscal,
        es_pep=cliente.es_pep,
        cargo_pep=cliente.cargo_pep,
        sector_economico=cliente.sector_economico,
        actividad_economica=cliente.actividad_economica,
        vinculos_pep=0,
        origen_fondos_documentado=True if cliente.origen_fondos else False
    )
    riesgo_result = riesgo_service.calcular_riesgo(riesgo_request)

    if cliente.es_pep:
        requiere_gerencial = True
        nivel_riesgo = NivelRiesgo.ALTO
    else:
        requiere_gerencial = riesgo_result.nivel_riesgo == NivelRiesgo.ALTO
        nivel_riesgo = riesgo_result.nivel_riesgo

    numero_expediente = generar_numero_expediente()
    db_expediente = Expediente(
        cliente_id=db_cliente.id,
        numero_expediente=numero_expediente,
        nivel_riesgo=nivel_riesgo,
        score_riesgo=riesgo_result.score_total,
        variables_riesgo=riesgo_result.variables,
        estado="pendiente_gerencia" if cliente.es_pep else "borrador",
        requiere_aprobacion_gerencial=requiere_gerencial,
        created_by=current_user.get("user_id")
    )
    db.add(db_expediente)

    evento = EventoAuditoria(
        expediente_id=None,
        usuario=current_user.get("user_id", "system"),
        accion="CREAR_CLIENTE_Y_EXPEDIENTE",
        detalles={
            "cliente_id": db_cliente.id,
            "numero_expediente": numero_expediente,
            "es_pep": cliente.es_pep,
            "nivel_riesgo": nivel_riesgo.value if hasattr(nivel_riesgo, 'value') else nivel_riesgo,
            "score_riesgo": riesgo_result.score_total
        }
    )
    db.add(evento)

    db.commit()
    db.refresh(db_cliente)
    return db_cliente


@router.put("/{cliente_id}", response_model=ClienteResponse)
def actualizar_cliente(
    cliente_id: int,
    cliente_update: ClienteUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    update_data = cliente_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cliente, field, value)

    db.commit()
    db.refresh(cliente)
    return cliente


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    db.delete(cliente)
    db.commit()
    return None
