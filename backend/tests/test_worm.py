"""Tests de inmutabilidad WORM de eventos de auditoria - issue #91 (Ley 23 Art. 21)."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.models.models import AuditoriaInmutableError, EventoAuditoria


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def _crear_evento(session: Session) -> EventoAuditoria:
    evento = EventoAuditoria(
        usuario="oficial",
        accion="CREAR_EXPEDIENTE",
        detalles={"numero": "EDD-TEST-0001"},
        ip_address="127.0.0.1",
    )
    session.add(evento)
    session.commit()
    return evento


class TestAuditoriaWORM:

    def test_crear_evento_funciona(self, db_session):
        evento = _crear_evento(db_session)
        assert evento.id is not None

    def test_modificar_evento_falla(self, db_session):
        evento = _crear_evento(db_session)
        evento.accion = "ACCION_ALTERADA"
        with pytest.raises(AuditoriaInmutableError):
            db_session.commit()
        db_session.rollback()
        db_session.refresh(evento)
        assert evento.accion == "CREAR_EXPEDIENTE"

    def test_modificar_detalles_falla(self, db_session):
        evento = _crear_evento(db_session)
        evento.detalles = {"numero": "FALSIFICADO"}
        with pytest.raises(AuditoriaInmutableError):
            db_session.commit()
        db_session.rollback()

    def test_eliminar_evento_falla(self, db_session):
        evento = _crear_evento(db_session)
        db_session.delete(evento)
        with pytest.raises(AuditoriaInmutableError):
            db_session.commit()
        db_session.rollback()
        assert db_session.query(EventoAuditoria).count() == 1
