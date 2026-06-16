import httpx
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.models import FuncionarioPublico
import csv
import io


class DatosAbiertosService:

    BASE_URL = settings.datos_abiertos_base_url
    DOWNLOAD_BASE = settings.datos_abiertos_download_base

    DATASETS_CONOCIDOS = {
        "sbp_designaciones_2026": "sbp-designacion-de-funciones-2026",
        "sbp_designaciones_2025": "sbp-designacion-de-funciones-2025",
    }

    async def obtener_datasets_planilla(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/action/package_search",
                    params={"q": "planilla", "rows": 20},
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()

                if data.get("success"):
                    results = data.get("result", {}).get("results", [])
                    return [{
                        "name": r.get("name"),
                        "title": r.get("title"),
                        "organization": r.get("organization", {}).get("title") if r.get("organization") else None,
                        "resources": r.get("resources", [])
                    } for r in results[:10]]
                return []
            except Exception as e:
                print(f"Error al obtener datasets: {e}")
                return []

    async def descargar_csv_funcionarios(self, resource_id: int) -> List[Dict[str, Any]]:
        url = f"{self.DOWNLOAD_BASE}/{resource_id}/csv"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=30.0)
                response.raise_for_status()

                contenido = response.text

                reader = csv.DictReader(io.StringIO(contenido))

                registros = []
                for row in reader:
                    registros.append({
                        "posicion": row.get("Posicion", ""),
                        "nombre": row.get("Nombre", ""),
                        "apellido": row.get("Apellido", ""),
                        "cedula": row.get("Cedula", ""),
                        "cargo_permanente": row.get("Cargo permanente", ""),
                        "cargo_designacion": row.get("Cargo designación", ""),
                        "fecha_inicio": row.get("Fecha inicio", ""),
                        "fecha_final": row.get("Fecha final", ""),
                        "numero_resolucion": row.get("Número de resolución", "")
                    })

                return registros

            except Exception as e:
                print(f"Error al descargar CSV {resource_id}: {e}")
                return []

    def sincronizar_funcionarios(self, db: Session, registros: List[Dict[str, Any]], institucion: str) -> int:
        count = 0

        for reg in registros:
            try:
                cedula = reg.get("cedula", "").strip()
                if not cedula:
                    continue

                existente = db.query(FuncionarioPublico).filter(
                    FuncionarioPublico.cedula == cedula,
                    FuncionarioPublico.numero_resolucion == reg.get("numero_resolucion")
                ).first()

                if existente:
                    existente.nombre = reg.get("nombre", "")
                    existente.apellido = reg.get("apellido", "")
                    existente.cargo_permanente = reg.get("cargo_permanente", "")
                    existente.cargo_designacion = reg.get("cargo_designacion", "")
                    existente.fecha_inicio = self._parse_date(reg.get("fecha_inicio"))
                    existente.fecha_final = self._parse_date(reg.get("fecha_final"))
                    existente.institucion = institucion
                    existente.downloaded_at = datetime.utcnow()
                else:
                    nuevo = FuncionarioPublico(
                        cedula=cedula,
                        nombre=reg.get("nombre", ""),
                        apellido=reg.get("apellido", ""),
                        cargo_permanente=reg.get("cargo_permanente", ""),
                        cargo_designacion=reg.get("cargo_designacion", ""),
                        institucion=institucion,
                        fecha_inicio=self._parse_date(reg.get("fecha_inicio")),
                        fecha_final=self._parse_date(reg.get("fecha_final")),
                        numero_resolucion=reg.get("numero_resolucion", ""),
                        es_pep=self._es_pep_por_cargo(reg.get("cargo_designacion", "")),
                        nivel_cargo=self._clasificar_nivel_cargo(reg.get("cargo_designacion", "")),
                        source="datosabiertos.gob.pa"
                    )
                    db.add(nuevo)
                    count += 1

            except Exception as e:
                print(f"Error al sincronizar registro: {e}")
                continue

        db.commit()
        return count

    def _parse_date(self, date_str: str):
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str.strip(), "%Y-%m-%d")
        except:
            try:
                return datetime.strptime(date_str.strip(), "%d/%m/%Y")
            except:
                return None

    def _es_pep_por_cargo(self, cargo: str) -> bool:
        if not cargo:
            return False
        cargo_lower = cargo.lower()

        palabras_pep = [
            "director", "gerente", "secretario", "viceministro", "subsecretario",
            "presidente", "vice", "jefe", "coordinador", "supervisor",
            "encargado", "magistrado", "juez", "fiscal", "embajador",
            "diputado", "senador", "governador", "militar", "general",
            "coronel", "capitan", "almirante"
        ]

        for palabra in palabras_pep:
            if palabra in cargo_lower:
                return True
        return False

    def _clasificar_nivel_cargo(self, cargo: str) -> str:
        if not cargo:
            return "bajo"
        cargo_lower = cargo.lower()

        alto = ["director general", "gerente general", "secretario general",
                "presidente", "vicepresidente", "primer ministro", "ministro",
                "magistrado", "juez", "fiscal", "embajador", "diputado", "senador"]

        medio = ["director", "gerente", "secretario", "subsecretario",
                "viceministro", "subdirector", "subgerente", "jefe",
                "coordinador", "supervisor"]

        for c in alto:
            if c in cargo_lower:
                return "alto"

        for c in medio:
            if c in cargo_lower:
                return "medio"

        return "bajo"


datos_abiertos_service = DatosAbiertosService()
