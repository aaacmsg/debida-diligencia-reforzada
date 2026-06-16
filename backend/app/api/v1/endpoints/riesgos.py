from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.schemas.schemas import CalculoRiesgoRequest, CalculoRiesgoResponse
from app.services.riesgo_service import riesgo_service

router = APIRouter()


@router.post("/calcular", response_model=CalculoRiesgoResponse)
def calcular_riesgo(
    data: CalculoRiesgoRequest,
    current_user: dict = Depends(get_current_user)
):
    resultado = riesgo_service.calcular_riesgo(data)
    return resultado
