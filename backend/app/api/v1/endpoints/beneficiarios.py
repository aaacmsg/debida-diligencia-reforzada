from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import BeneficiarioFinal, Cliente, EventoAuditoria
from app.schemas.schemas import BeneficiarioFinalCreate, BeneficiarioFinalResponse

router = APIRouter()


@router.get("/{cliente_id}", response_model=List[BeneficiarioFinalResponse])
def listar_beneficiarios(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return db.query(BeneficiarioFinal).filter(BeneficiarioFinal.cliente_id == cliente_id).all()


@router.post("/{cliente_id}", response_model=BeneficiarioFinalResponse, status_code=status.HTTP_201_CREATED)
def crear_beneficiario(
    cliente_id: int,
    data: BeneficiarioFinalCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    total = db.query(BeneficiarioFinal).filter(
        BeneficiarioFinal.cliente_id == cliente_id
    ).with_entities(BeneficiarioFinal.porcentaje_participacion).all()
    suma_actual = sum(p[0] for p in total) if total else 0

    if suma_actual + data.porcentaje_participacion > 100:
        raise HTTPException(
            status_code=400,
            detail=f"La suma de participaciones no puede exceder 100%. Actual: {suma_actual}%"
        )

    db_bf = BeneficiarioFinal(cliente_id=cliente_id, **data.model_dump())
    db.add(db_bf)

    evento = EventoAuditoria(
        expediente_id=None,
        usuario=current_user.get("user_id", "system"),
        accion="CREAR_BENEFICIARIO_FINAL",
        detalles={"cliente_id": cliente_id, "nombre": data.nombre, "porcentaje": data.porcentaje_participacion}
    )
    db.add(evento)

    db.commit()
    db.refresh(db_bf)
    return db_bf


@router.delete("/{cliente_id}/{beneficiario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_beneficiario(
    cliente_id: int,
    beneficiario_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    bf = db.query(BeneficiarioFinal).filter(
        BeneficiarioFinal.id == beneficiario_id,
        BeneficiarioFinal.cliente_id == cliente_id
    ).first()
    if not bf:
        raise HTTPException(status_code=404, detail="Beneficiario no encontrado")

    db.delete(bf)

    evento = EventoAuditoria(
        expediente_id=None,
        usuario=current_user.get("user_id", "system"),
        accion="ELIMINAR_BENEFICIARIO_FINAL",
        detalles={"cliente_id": cliente_id, "nombre": bf.nombre}
    )
    db.add(evento)
    db.commit()
    return None
