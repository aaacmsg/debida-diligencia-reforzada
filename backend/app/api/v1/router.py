from fastapi import APIRouter
from app.api.v1.endpoints import (
    clientes,
    expedientes,
    documentos,
    riesgos,
    pep,
    reportes,
    auth,
    beneficiarios,
    configuracion,
    alertas
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(clientes.router, prefix="/clientes", tags=["clientes"])
api_router.include_router(expedientes.router, prefix="/expedientes", tags=["expedientes"])
api_router.include_router(documentos.router, prefix="/documentos", tags=["documentos"])
api_router.include_router(beneficiarios.router, prefix="/beneficiarios", tags=["beneficiarios"])
api_router.include_router(riesgos.router, prefix="/riesgos", tags=["riesgos"])
api_router.include_router(pep.router, prefix="/pep", tags=["pep"])
api_router.include_router(reportes.router, prefix="/reportes", tags=["reportes"])
api_router.include_router(configuracion.router, prefix="/configuracion", tags=["configuracion"])
api_router.include_router(alertas.router, prefix="/alertas", tags=["alertas"])
