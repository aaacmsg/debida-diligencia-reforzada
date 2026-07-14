"""Test de integracion del endpoint de exportacion PDF - issue #92.

Requiere base de datos accesible; si no hay, se salta.
"""
import time

import pytest
from sqlalchemy import text

from app.core.database import engine

try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    _DB_DISPONIBLE = True
except Exception:
    _DB_DISPONIBLE = False

pytestmark = pytest.mark.skipif(not _DB_DISPONIBLE, reason="requiere base de datos accesible")

if _DB_DISPONIBLE:
    from fastapi.testclient import TestClient
    from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def admin_token(client):
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


class TestExportarPDF:

    def test_exportar_pdf_de_expediente(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        # Cliente nuevo con cedula unica -> auto-crea expediente
        cedula = f"9-{int(time.time()) % 10000000:07d}-001"
        resp = client.post("/api/v1/clientes/", json={
            "tipo_persona": "natural",
            "nombre": "Cliente",
            "apellido": "PDFTest",
            "tipo_identificacion": "cedula",
            "numero_identificacion": cedula,
            "pais_residencia": "Panama",
        }, headers=headers)
        assert resp.status_code == 201, resp.text
        cliente_id = resp.json()["id"]

        expedientes = client.get("/api/v1/expedientes/", headers=headers).json()
        exp = next(e for e in expedientes if e["cliente_id"] == cliente_id)

        resp = client.get(f"/api/v1/expedientes/{exp['id']}/pdf", headers=headers)
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"
        assert resp.content.startswith(b"%PDF")
        assert exp["numero_expediente"] in resp.headers["content-disposition"]

    def test_pdf_expediente_inexistente_404(self, client, admin_token):
        resp = client.get("/api/v1/expedientes/999999/pdf",
                          headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 404

    def test_pdf_sin_auth_401(self, client):
        resp = client.get("/api/v1/expedientes/1/pdf")
        assert resp.status_code == 401
