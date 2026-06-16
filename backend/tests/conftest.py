import pytest
from datetime import timedelta
from app.core.config import Settings
from app.services.riesgo_service import RiesgoService
from app.schemas.schemas import CalculoRiesgoRequest, CalculoRiesgoResponse


@pytest.fixture
def test_settings():
    return Settings(
        database_url="sqlite:///:memory:",
        secret_key="test-secret-key-for-testing-only",
        algorithm="HS256",
        access_token_expire_minutes=60,
        score_pais_peso=0.25,
        score_cargo_peso=0.30,
        score_sector_peso=0.15,
        score_vinculos_peso=0.20,
        score_origen_fondos_peso=0.10,
        fuzzy_match_threshold=85,
        riesgo_bajo_max=35,
        riesgo_medio_max=65,
    )


@pytest.fixture
def riesgo_service(test_settings) -> RiesgoService:
    return RiesgoService()


@pytest.fixture
def riesgo_bajo_input() -> CalculoRiesgoRequest:
    return CalculoRiesgoRequest(
        pais_residencia="espana",
        pais_residencia_fiscal="espana",
        es_pep=False,
        sector_economico="educacion",
        actividad_economica="profesor",
        vinculos_pep=0,
        origen_fondos_documentado=True,
    )


@pytest.fixture
def riesgo_alto_input() -> CalculoRiesgoRequest:
    return CalculoRiesgoRequest(
        pais_residencia="iran",
        pais_residencia_fiscal="iran",
        es_pep=True,
        cargo_pep="Presidente",
        sector_economico="construccion",
        actividad_economica="constructora",
        vinculos_pep=5,
        origen_fondos_documentado=False,
    )


@pytest.fixture
def riesgo_medio_input() -> CalculoRiesgoRequest:
    return CalculoRiesgoRequest(
        pais_residencia="panama",
        pais_residencia_fiscal="panama",
        es_pep=True,
        cargo_pep="Coordinador",
        sector_economico="comercio internacional",
        actividad_economica="importacion",
        vinculos_pep=1,
        origen_fondos_documentado=True,
    )
