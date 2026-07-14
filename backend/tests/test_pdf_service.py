"""Tests del servicio de exportacion PDF de expedientes - issue #92."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.models.models import (
    BeneficiarioFinal,
    Cliente,
    EstadoExpediente,
    EventoAuditoria,
    Expediente,
    NivelRiesgo,
    TipoIdentificacion,
    TipoPersona,
)
from app.services.pdf_service import generar_pdf_expediente


@pytest.fixture
def expediente_completo():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        cliente = Cliente(
            tipo_persona=TipoPersona.JURIDICA,
            nombre="Constructora Test",
            razon_social="Constructora Test S.A.",
            tipo_identificacion=TipoIdentificacion.RUC,
            numero_identificacion="155600000-1-2020",
            pais_residencia="Panama",
            es_pep=False,
            sector_economico="Construccion",
            ingresos_anuales=1000000.0,
        )
        db.add(cliente)
        db.flush()
        db.add(BeneficiarioFinal(
            cliente_id=cliente.id, nombre="Juan", apellido="Gomez",
            numero_identificacion="8-702-3355", porcentaje_participacion=40,
            tipo_control="Accionista", es_pep=True,
        ))
        expediente = Expediente(
            cliente_id=cliente.id,
            numero_expediente="EDD-TEST-PDF01",
            nivel_riesgo=NivelRiesgo.ALTO,
            score_riesgo=71.5,
            estado=EstadoExpediente.PENDIENTE_GERENCIA,
            requiere_aprobacion_gerencial=True,
        )
        db.add(expediente)
        db.flush()
        db.add(EventoAuditoria(
            expediente_id=expediente.id, usuario="oficial",
            accion="CREAR_EXPEDIENTE", ip_address="127.0.0.1",
        ))
        db.commit()
        db.refresh(expediente)
        db.refresh(cliente)
        yield expediente, cliente


class TestPdfService:

    def test_genera_pdf_valido(self, expediente_completo):
        expediente, cliente = expediente_completo
        pdf = generar_pdf_expediente(expediente, cliente,
                                     expediente.documentos, expediente.eventos)
        assert isinstance(pdf, bytes)
        assert pdf.startswith(b"%PDF")
        assert len(pdf) > 1000

    def test_pdf_sin_datos_opcionales(self, expediente_completo):
        """No debe explotar con campos None (patrimonio, comentario, etc.)."""
        expediente, cliente = expediente_completo
        cliente.patrimonio = None
        cliente.origen_fondos = None
        expediente.score_riesgo = None
        pdf = generar_pdf_expediente(expediente, cliente, [], [])
        assert pdf.startswith(b"%PDF")

    def test_pdf_con_caracteres_no_latinos(self, expediente_completo):
        """Caracteres fuera de latin-1 se reemplazan en vez de fallar."""
        expediente, cliente = expediente_completo
        cliente.nombre = "Test 日本 Ω"
        pdf = generar_pdf_expediente(expediente, cliente, [], [])
        assert pdf.startswith(b"%PDF")
