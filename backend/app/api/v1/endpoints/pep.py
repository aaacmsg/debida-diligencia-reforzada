from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import asyncio
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.schemas import PEPSearchRequest, PEPSearchResponse
from app.services.pep_service import pep_service
from app.services.datos_abiertos_service import datos_abiertos_service

router = APIRouter()

INSTITUCIONES_CONOCIDAS = {
    2310: "SBP - Designaciones 2026",
    2089: "SBP - Designaciones 2025",
}


@router.post("/buscar", response_model=List[PEPSearchResponse])
def buscar_pep(
    search: PEPSearchRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    resultados = pep_service.buscar_funcionario(db, search)
    return resultados


@router.get("/funcionarios/count")
def contar_funcionarios(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from app.models.models import FuncionarioPublico
    total = db.query(FuncionarioPublico).count()
    pep_count = db.query(FuncionarioPublico).filter(
        FuncionarioPublico.es_pep == True
    ).count()

    return {
        "total_funcionarios": total,
        "clasificados_pep": pep_count
    }


@router.get("/cargos")
def listar_cargos_pep():
    cargos = [
        {
            "categoria": "Poder Ejecutivo",
            "cargos": [
                "Presidente de la República",
                "Vicepresidente de la República",
                "Ministro de Estado",
                "Viceministro",
                "Director General de Entidad Autónoma",
                "Secretario General de Ministerio",
            ]
        },
        {
            "categoria": "Poder Legislativo",
            "cargos": [
                "Diputado de la Asamblea Nacional",
                "Presidente de la Asamblea Nacional",
                "Vicepresidente de la Asamblea Nacional",
                "Secretario de la Asamblea Nacional",
            ]
        },
        {
            "categoria": "Poder Judicial",
            "cargos": [
                "Magistrado de la Corte Suprema de Justicia",
                "Juez de Circuito",
                "Juez Municipal",
                "Fiscal Superior",
                "Fiscal de Circuito",
                "Procurador General de la Nación",
                "Procurador de la Administración",
            ]
        },
        {
            "categoria": "Órganos Autónomos y Entidades Reguladoras",
            "cargos": [
                "Superintendente de Bancos",
                "Superintendente de Valores",
                "Superintendente de Seguros",
                "Director de la Autoridad Nacional de Ingresos (ANI)",
                "Director de la Caja de Seguro Social (CSS)",
                "Contralor General de la República",
                "Subcontralor General de la República",
                "Defensor del Pueblo",
            ]
        },
        {
            "categoria": "Gobiernos Locales",
            "cargos": [
                "Alcalde",
                "Representante de Corregimiento",
                "Gobernador de Provincia",
            ]
        },
        {
            "categoria": "Cuerpo Diplomático",
            "cargos": [
                "Embajador",
                "Cónsul General",
                "Representante Permanente ante Organismos Internacionales",
            ]
        },
        {
            "categoria": "Empresas Públicas",
            "cargos": [
                "Gerente General de Empresa Pública",
                "Director de Empresa Pública",
                "Miembro de Junta Directiva de Empresa Pública",
            ]
        },
    ]
    return cargos


@router.post("/sincronizar")
def sincronizar_funcionarios(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    total_sincronizados = 0
    errores = []

    for resource_id, institucion in INSTITUCIONES_CONOCIDAS.items():
        try:
            registros = asyncio.run(
                datos_abiertos_service.descargar_csv_funcionarios(resource_id)
            )
            if registros:
                count = datos_abiertos_service.sincronizar_funcionarios(
                    db, registros, institucion
                )
                total_sincronizados += count
        except Exception as e:
            errores.append({"resource_id": resource_id, "error": str(e)})

    from app.models.models import FuncionarioPublico
    total = db.query(FuncionarioPublico).count()

    return {
        "sincronizados": total_sincronizados,
        "total_funcionarios": total,
        "errores": errores
    }
