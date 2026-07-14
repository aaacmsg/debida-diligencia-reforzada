from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.models import Configuracion

router = APIRouter()


@router.get("/")
def listar_configuracion(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    configs = db.query(Configuracion).all()
    return {c.clave: c.valor for c in configs}


@router.put("/")
def actualizar_configuracion(
    data: Dict[str, str],
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles())  # solo admin configura el sistema
):
    for clave, valor in data.items():
        config = db.query(Configuracion).filter(Configuracion.clave == clave).first()
        if config:
            config.valor = valor
            config.updated_by = current_user.get("user_id")
        else:
            config = Configuracion(
                clave=clave,
                valor=valor,
                updated_by=current_user.get("user_id")
            )
            db.add(config)

    db.commit()
    return {"status": "ok"}
