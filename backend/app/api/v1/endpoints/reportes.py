from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from datetime import datetime, timedelta
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.models import Expediente, Cliente, Documento, EventoAuditoria, BeneficiarioFinal, EstadoExpediente, NivelRiesgo

router = APIRouter()


@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    total_expedientes = db.query(Expediente).count()

    por_estado = db.query(
        Expediente.estado,
        func.count(Expediente.id)
    ).group_by(Expediente.estado).all()

    por_riesgo = db.query(
        Expediente.nivel_riesgo,
        func.count(Expediente.id)
    ).group_by(Expediente.nivel_riesgo).all()

    return {
        "total_expedientes": total_expedientes,
        "por_estado": {estado.value: count for estado, count in por_estado},
        "por_riesgo": {riesgo.value: count for riesgo, count in por_riesgo}
    }


@router.get("/expedientes")
def reporte_expedientes(
    skip: int = 0,
    limit: int = 50,
    estado: Optional[str] = None,
    riesgo: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(Expediente, Cliente).join(Cliente)

    if estado:
        query = query.filter(Expediente.estado == estado)
    if riesgo:
        query = query.filter(Expediente.nivel_riesgo == riesgo)

    resultados = query.offset(skip).limit(limit).all()

    return [{
        "id": exp.id,
        "numero_expediente": exp.numero_expediente,
        "cliente_nombre": f"{cli.nombre} {cli.apellido or ''}",
        "estado": exp.estado.value,
        "nivel_riesgo": exp.nivel_riesgo.value,
        "score_riesgo": exp.score_riesgo,
        "created_at": exp.created_at.isoformat() if exp.created_at else None
    } for exp, cli in resultados]


@router.get("/auditoria")
def reporte_auditoria(
    expediente_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    # CA-04.1: trazabilidad solo para Oficial de Cumplimiento y Admin
    current_user: dict = Depends(require_roles("oficial_cumplimiento"))
):
    query = db.query(EventoAuditoria)

    if expediente_id:
        query = query.filter(EventoAuditoria.expediente_id == expediente_id)

    eventos = query.order_by(
        EventoAuditoria.created_at.desc()
    ).offset(skip).limit(limit).all()

    return [{
        "id": e.id,
        "expediente_id": e.expediente_id,
        "usuario": e.usuario,
        "accion": e.accion,
        "detalles": e.detalles,
        "created_at": e.created_at.isoformat() if e.created_at else None
    } for e in eventos]


@router.get("/export/csv")
def exportar_csv(
    estado: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(Expediente, Cliente).join(Cliente)

    if estado:
        query = query.filter(Expediente.estado == estado)

    resultados = query.all()

    csv_lines = ["numero_expediente,cliente,estado,riesgo,score,fecha_creacion"]
    for exp, cli in resultados:
        cliente_nombre = f"{cli.nombre} {cli.apellido or ''}".replace(",", " ")
        linea = f"{exp.numero_expediente},{cliente_nombre},{exp.estado.value},{exp.nivel_riesgo.value},{exp.score_riesgo or 0},{exp.created_at}"
        csv_lines.append(linea)

    csv_content = "\n".join(csv_lines)
    filename = f"expedientes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/grafo")
def grafo_relaciones(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    clientes = db.query(Cliente).limit(50).all()

    nodes = []
    edges = []
    added_ids = set()

    for c in clientes:
        node_id = f"cliente_{c.id}"
        nodes.append({
            "id": node_id,
            "label": f"{c.nombre} {c.apellido or ''}",
            "type": "cliente",
            "riesgo": None,
            "es_pep": c.es_pep
        })
        added_ids.add(node_id)

        for bf in c.beneficiarios_finales:
            bf_id = f"persona_{bf.id}"
            if bf_id not in added_ids:
                nodes.append({
                    "id": bf_id,
                    "label": f"{bf.nombre} {bf.apellido or ''}",
                    "type": "persona",
                    "riesgo": None,
                    "es_pep": bf.es_pep
                })
                added_ids.add(bf_id)

            edges.append({
                "source": node_id,
                "target": bf_id,
                "label": f"{bf.porcentaje_participacion}%",
                "type": "accionista"
            })

        for exp in c.expedientes:
            for doc in exp.documentos:
                doc_id = f"doc_{doc.id}"
                if doc_id not in added_ids:
                    nodes.append({
                        "id": doc_id,
                        "label": doc.nombre_archivo[:20],
                        "type": "documento",
                        "riesgo": None,
                        "es_pep": False
                    })
                    added_ids.add(doc_id)

                edges.append({
                    "source": node_id,
                    "target": doc_id,
                    "label": doc.tipo_documento,
                    "type": "documento"
                })

    return {
        "nodes": nodes,
        "edges": edges
    }