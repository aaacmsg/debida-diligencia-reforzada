"""Tests de integracion de seguridad via API (RBAC #89, rate limit #90, refresh #97).

Requieren una base de datos accesible (docker-compose db o el servicio postgres del CI).
Si no hay DB se saltan automaticamente.
"""
import pytest
from sqlalchemy import text

from app.core.database import engine
from app.core.security import limiter

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


def _login(client, username, password):
    return client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )


def _asegurar_usuario(client, admin_token, username, rol):
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": f"{username}@test.pa",
            "password": f"{username}123",
            "full_name": f"Usuario {rol}",
            "rol": rol,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    # 200 = creado, 400 = ya existia de una corrida anterior
    assert resp.status_code in (200, 400), resp.text


@pytest.fixture(scope="module")
def client():
    limiter.reset()
    # context manager para disparar el startup (crea admin/admin123)
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def admin_login(client):
    """Un solo login de admin para todo el modulo (cuida el rate limit)."""
    resp = _login(client, "admin", "admin123")
    assert resp.status_code == 200, resp.text
    return resp.json()


@pytest.fixture(scope="module")
def tokens(client, admin_login):
    """Tokens de los 3 roles con el minimo de llamadas a /login."""
    admin_token = admin_login["access_token"]
    _asegurar_usuario(client, admin_token, "test_oficial", "oficial_cumplimiento")
    _asegurar_usuario(client, admin_token, "test_gerencia", "alta_gerencia")
    oficial = _login(client, "test_oficial", "test_oficial123").json()["access_token"]
    gerencia = _login(client, "test_gerencia", "test_gerencia123").json()["access_token"]
    return {"admin": admin_token, "oficial": oficial, "gerencia": gerencia}


class TestSeguridadAPI:

    def test_login_devuelve_refresh_token(self, admin_login):
        assert admin_login["access_token"]
        assert admin_login["refresh_token"]

    def test_refresh_emite_nuevos_tokens(self, client, admin_login):
        resp = client.post("/api/v1/auth/refresh",
                           json={"refresh_token": admin_login["refresh_token"]})
        assert resp.status_code == 200
        body = resp.json()
        assert body["access_token"]
        assert body["refresh_token"]

    def test_refresh_con_access_token_falla(self, client, admin_login):
        resp = client.post("/api/v1/auth/refresh",
                           json={"refresh_token": admin_login["access_token"]})
        assert resp.status_code == 401

    def test_register_sin_admin_da_403(self, client, tokens):
        resp = client.post(
            "/api/v1/auth/register",
            json={"username": "x", "email": "x@test.pa", "password": "x12345", "rol": "admin"},
            headers={"Authorization": f"Bearer {tokens['gerencia']}"},
        )
        assert resp.status_code == 403

    def test_rbac_aprobar_requiere_alta_gerencia(self, client, tokens):
        # oficial: bloqueado por RBAC antes de tocar el expediente
        resp = client.post(
            "/api/v1/expedientes/999999/aprobar",
            params={"comentario": "test"},
            headers={"Authorization": f"Bearer {tokens['oficial']}"},
        )
        assert resp.status_code == 403

        # gerencia: pasa RBAC y llega al 404 de expediente inexistente
        resp = client.post(
            "/api/v1/expedientes/999999/aprobar",
            params={"comentario": "test"},
            headers={"Authorization": f"Bearer {tokens['gerencia']}"},
        )
        assert resp.status_code == 404

    def test_rbac_auditoria_solo_oficial_y_admin(self, client, tokens):
        resp = client.get("/api/v1/reportes/auditoria",
                          headers={"Authorization": f"Bearer {tokens['oficial']}"})
        assert resp.status_code == 200

        resp = client.get("/api/v1/reportes/auditoria",
                          headers={"Authorization": f"Bearer {tokens['gerencia']}"})
        assert resp.status_code == 403

    def test_zz_rate_limit_en_login(self, client):
        """Ultimo test del modulo: agota el limite de login configurado y espera 429."""
        from app.core.config import settings
        limite = int(settings.login_rate_limit.split("/")[0])
        if limite > 30:
            pytest.skip(f"LOGIN_RATE_LIMIT={settings.login_rate_limit} (elevado para E2E)")
        limiter.reset()
        codigos = []
        for _ in range(limite + 2):
            resp = _login(client, "admin", "clave-incorrecta")
            codigos.append(resp.status_code)
        assert codigos[0] == 401
        assert 429 in codigos, f"no aparecio 429 en {codigos}"
        limiter.reset()
