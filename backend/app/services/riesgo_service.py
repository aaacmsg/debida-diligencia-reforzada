from typing import Dict, Optional
from app.core.config import settings
from app.schemas.schemas import (
    CalculoRiesgoRequest,
    CalculoRiesgoResponse,
    NivelRiesgo
)


class RiesgoService:

    PAISES_ALTO_RIESGO = [
        "iran", "corea del norte", "siria", "cuba", "venezuela", "myanmar",
        "afganistan", "sudan", "zimbabwe", "yemen"
    ]

    TERRITORIOS_OFFSHORE = [
        "panama", "belize", "islas caiman", "virgenes britanicas",
        "samoa", "mauricio", "seychelles", "dominica"
    ]

    CARGOS_PEP_ALTO = [
        "presidente", "vicepresidente", "primer ministro", "primer ministro",
        "ministro", "viceministro", "secretario", "subsecretario",
        "director", "subdirector", "gerente general", "gerente",
        "magistrado", "juez", "fiscal", "embajador", "consejero",
        "diputado", "senador", "parlamentario", "governador",
        "jefe de estado", "jefe de gobierno", "militar", "general",
        "coronel", "capitan", "almirante", "comandante"
    ]

    CARGOS_PEP_MEDIO = [
        "jefe", "subjefe", "director adjoint", "gerente adjoint",
        "supervisor", "coordinador", "asesor", "consejero",
        "secretario general", "vocero", "portavoz"
    ]

    SECTORES_ALTO_RIESGO = [
        "construccion", "bienes raiz", "real estate", "inmuebles",
        "metales preciosos", "oro", "plata", "diamantes",
        "arte", "antiguedades", "vehiculos de lujo", "yates",
        "casinos", "apuestas", "loterias", "transferencia de fondos",
        "compensacion", "cambio de moneda", "jurado juri"
    ]

    SECTORES_MEDIO_RIESGO = [
        "comercio internacional", "importacion", "exportacion",
        "transporte", "logistica", "almacenamiento",
        "servicios financieros", "inversiones"
    ]

    def calcular_riesgo(self, data: CalculoRiesgoRequest) -> CalculoRiesgoResponse:
        pais_score = self._calcular_score_pais(data)
        cargo_score = self._calcular_score_cargo(data)
        sector_score = self._calcular_score_sector(data)
        vinculos_score = self._calcular_score_vinculos(data)
        origen_score = self._calcular_score_origen_fondos(data)

        score_total = (
            pais_score * settings.score_pais_peso +
            cargo_score * settings.score_cargo_peso +
            sector_score * settings.score_sector_peso +
            vinculos_score * settings.score_vinculos_peso +
            origen_score * settings.score_origen_fondos_peso
        )

        nivel = self._determinar_nivel(score_total)

        variables = {
            "pais": {"score": pais_score, "detalle": self._get_pais_detalle(data)},
            "cargo": {"score": cargo_score, "detalle": self._get_cargo_detalle(data)},
            "sector": {"score": sector_score, "detalle": self._get_sector_detalle(data)},
            "vinculos": {"score": vinculos_score, "detalle": self._get_vinculos_detalle(data)},
            "origen_fondos": {"score": origen_score, "detalle": self._get_origen_detalle(data)}
        }

        ponderacion = {
            "pais": settings.score_pais_peso,
            "cargo": settings.score_cargo_peso,
            "sector": settings.score_sector_peso,
            "vinculos": settings.score_vinculos_peso,
            "origen_fondos": settings.score_origen_fondos_peso
        }

        return CalculoRiesgoResponse(
            score_total=round(score_total, 2),
            nivel_riesgo=nivel,
            variables=variables,
            ponderacion=ponderacion
        )

    def _calcular_score_pais(self, data: CalculoRiesgoRequest) -> float:
        paises_riesgo = data.pais_residencia_fiscal or data.pais_residencia or ""
        pais_lower = paises_riesgo.lower()

        for pais in self.PAISES_ALTO_RIESGO:
            if pais in pais_lower:
                return 100

        for territorio in self.TERRITORIOS_OFFSHORE:
            if territorio in pais_lower:
                return 80

        return 25

    def _calcular_score_cargo(self, data: CalculoRiesgoRequest) -> float:
        if not data.es_pep:
            return 10

        cargo = (data.cargo_pep or "").lower()

        for cargo_alto in self.CARGOS_PEP_ALTO:
            if cargo_alto in cargo:
                return 100

        for cargo_medio in self.CARGOS_PEP_MEDIO:
            if cargo_medio in cargo:
                return 60

        return 40

    def _calcular_score_sector(self, data: CalculoRiesgoRequest) -> float:
        sector = (data.sector_economico or data.actividad_economica or "").lower()

        for s in self.SECTORES_ALTO_RIESGO:
            if s in sector:
                return 100

        for s in self.SECTORES_MEDIO_RIESGO:
            if s in sector:
                return 50

        return 20

    def _calcular_score_vinculos(self, data: CalculoRiesgoRequest) -> float:
        if data.vinculos_pep == 0:
            return 10
        elif data.vinculos_pep == 1:
            return 40
        elif data.vinculos_pep <= 3:
            return 70
        else:
            return 100

    def _calcular_score_origen_fondos(self, data: CalculoRiesgoRequest) -> float:
        if data.origen_fondos_documentado:
            return 10
        return 80

    def _determinar_nivel(self, score: float) -> NivelRiesgo:
        if score <= settings.riesgo_bajo_max:
            return NivelRiesgo.BAJO
        elif score <= settings.riesgo_medio_max:
            return NivelRiesgo.MEDIO
        return NivelRiesgo.ALTO

    def _get_pais_detalle(self, data: CalculoRiesgoRequest) -> dict:
        return {
            "pais_residencia": data.pais_residencia,
            "pais_residencia_fiscal": data.pais_residencia_fiscal
        }

    def _get_cargo_detalle(self, data: CalculoRiesgoRequest) -> dict:
        return {
            "es_pep": data.es_pep,
            "cargo": data.cargo_pep
        }

    def _get_sector_detalle(self, data: CalculoRiesgoRequest) -> dict:
        return {
            "sector_economico": data.sector_economico,
            "actividad_economica": data.actividad_economica
        }

    def _get_vinculos_detalle(self, data: CalculoRiesgoRequest) -> dict:
        return {
            "cantidad_vinculos_pep": data.vinculos_pep
        }

    def _get_origen_detalle(self, data: CalculoRiesgoRequest) -> dict:
        return {
            "documentado": data.origen_fondos_documentado
        }


riesgo_service = RiesgoService()
