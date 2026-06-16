from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from rapidfuzz import fuzz, process
from app.core.config import settings
from app.models.models import FuncionarioPublico, Cliente
from app.schemas.schemas import PEPSearchRequest, PEPSearchResponse


class PEPService:

    def __init__(self):
        self.threshold = settings.fuzzy_match_threshold

    def buscar_funcionario(
        self,
        db: Session,
        search: PEPSearchRequest
    ) -> List[PEPSearchResponse]:
        resultados = []

        query = db.query(FuncionarioPublico)

        if search.cedula:
            func = query.filter(
                FuncionarioPublico.cedula == search.cedula
            ).first()

            if func:
                return [PEPSearchResponse(
                    cedula=func.cedula,
                    nombre=func.nombre,
                    apellido=func.apellido,
                    cargo_designacion=func.cargo_designacion,
                    institucion=func.institucion,
                    score_similitud=100.0,
                    es_exacto=True
                )]

        if search.nombre or search.apellido:
            termino_busqueda = f"{search.nombre or ''} {search.apellido or ''}".strip().lower()
            palabras = termino_busqueda.split()

            filters = []
            for palabra in palabras:
                filters.append(
                    FuncionarioPublico.nombre.ilike(f"%{palabra}%")
                )
                filters.append(
                    FuncionarioPublico.apellido.ilike(f"%{palabra}%")
                )

            if filters:
                query = query.filter(or_(*filters))

            # Limit to 500 candidates before fuzzy matching
            candidatos = query.limit(500).all()

            matches = []
            for func in candidatos:
                nombre_completo = f"{func.nombre} {func.apellido}".lower()

                score_nombre = fuzz.ratio(termino_busqueda, nombre_completo)
                score_partial = fuzz.partial_ratio(termino_busqueda, nombre_completo)
                score_token = fuzz.token_set_ratio(termino_busqueda, nombre_completo)

                mejor_score = max(score_nombre, score_partial, score_token)

                if mejor_score >= self.threshold:
                    matches.append({
                        "funcionario": func,
                        "score": mejor_score,
                        "es_exacto": mejor_score == 100
                    })

            matches.sort(key=lambda x: x["score"], reverse=True)

            for match in matches[:20]:
                func = match["funcionario"]
                resultados.append(PEPSearchResponse(
                    cedula=func.cedula,
                    nombre=func.nombre,
                    apellido=func.apellido,
                    cargo_designacion=func.cargo_designacion,
                    institucion=func.institucion,
                    score_similitud=round(match["score"], 2),
                    es_exacto=match["es_exacto"]
                ))

        return resultados

    def clasificar_nivel_cargo(self, cargo: str) -> str:
        cargo_lower = cargo.lower()

        alto_cargo = [
            "presidente", "vicepresidente", "primer ministro",
            "ministro", "viceminist", "secretario general", "subsecretario",
            "director general", "gerente general", "subdirector general",
            "magistrado", "juez", "fiscal", "embajador", "diputado", "senador",
            "gobernador", "jefe de estado", "jefe de gobierno"
        ]

        medio_cargo = [
            "gerente", "director", "subdirector", "jefe de", "subgerente",
            "coordinador", "asesor", "supervisor", "encargado", "secretario"
        ]

        for c in alto_cargo:
            if c in cargo_lower:
                return "alto"

        for c in medio_cargo:
            if c in cargo_lower:
                return "medio"

        return "bajo"

    def verificar_cliente_en_funcionarios(
        self,
        db: Session,
        cliente: Cliente
    ) -> Optional[PEPSearchResponse]:
        nombre_completo = f"{cliente.nombre} {cliente.apellido or ''}".strip()
        cedula = cliente.numero_identificacion

        search_request = PEPSearchRequest(
            nombre=cliente.nombre,
            apellido=cliente.apellido,
            cedula=cedula
        )

        resultados = self.buscar_funcionario(db, search_request)

        for resultado in resultados:
            if resultado.cedula == cedula and resultado.score_similitud >= 95:
                return resultado

            if resultado.score_similitud >= 90:
                return resultado

        return None


pep_service = PEPService()