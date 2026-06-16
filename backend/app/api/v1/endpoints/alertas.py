from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Alerta, Expediente, Cliente, NivelRiesgo

router = APIRouter()


@router.get("/")
def listar_alertas(
    solo_no_leidas: bool = True,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(Alerta)
    if solo_no_leidas:
        query = query.filter(Alerta.leida == False)
    alertas = query.order_by(Alerta.created_at.desc()).limit(50).all()
    return [
        {
            "id": a.id,
            "expediente_id": a.expediente_id,
            "tipo_alerta": a.tipo_alerta,
            "mensaje": a.mensaje,
            "nivel": a.nivel,
            "leida": a.leida,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in alertas
    ]


@router.post("/generar")
def generar_alertas(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    count = 0

    expedientes_alto_riesgo = db.query(Expediente).filter(
        Expediente.nivel_riesgo == NivelRiesgo.ALTO,
        Expediente.estado.in_(["pendiente_revision", "pendiente_gerencia"])
    ).all()

    for exp in expedientes_alto_riesgo:
        existente = db.query(Alerta).filter(
            Alerta.expediente_id == exp.id,
            Alerta.tipo_alerta == "alto_riesgo",
            Alerta.leida == False
        ).first()
        if not existente:
            alerta = Alerta(
                expediente_id=exp.id,
                tipo_alerta="alto_riesgo",
                mensaje=f"Expediente {exp.numero_expediente} requiere atencion - Riesgo ALTO",
                nivel="alto",
            )
            db.add(alerta)
            count += 1

    from datetime import timedelta
    hace_6_meses = datetime.utcnow() - timedelta(days=180)
    expedientes_antiguos = db.query(Expediente).filter(
        Expediente.updated_at < hace_6_meses,
        Expediente.estado.in_(["aprobado", "borrador"])
    ).all()

    for exp in expedientes_antiguos:
        existente = db.query(Alerta).filter(
            Alerta.expediente_id == exp.id,
            Alerta.tipo_alerta == "actualizacion_pendiente",
            Alerta.leida == False
        ).first()
        if not existente:
            alerta = Alerta(
                expediente_id=exp.id,
                tipo_alerta="actualizacion_pendiente",
                mensaje=f"Expediente {exp.numero_expediente} requiere actualizacion (+6 meses sin cambios)",
                nivel="medio",
            )
            db.add(alerta)
            count += 1

    db.commit()
    return {"alertas_generadas": count}


@router.post("/{alerta_id}/leer")
def marcar_leida(
    alerta_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    alerta = db.query(Alerta).filter(Alerta.id == alerta_id).first()
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    alerta.leida = True
    db.commit()
    return {"status": "ok"}
