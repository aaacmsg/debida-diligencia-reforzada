"""Tests de RBAC (require_roles) - issue #89."""
import asyncio

import pytest
from fastapi import HTTPException

from app.core.security import require_roles


def _ejecutar(dependencia, roles):
    return asyncio.run(dependencia(current_user={"user_id": "test", "roles": roles}))


class TestRequireRoles:

    def test_rol_permitido_pasa(self):
        dep = require_roles("alta_gerencia")
        user = _ejecutar(dep, ["alta_gerencia"])
        assert user["user_id"] == "test"

    def test_admin_siempre_pasa(self):
        dep = require_roles("alta_gerencia")
        user = _ejecutar(dep, ["admin"])
        assert user["roles"] == ["admin"]

    def test_rol_no_permitido_da_403(self):
        dep = require_roles("alta_gerencia")
        with pytest.raises(HTTPException) as exc:
            _ejecutar(dep, ["oficial_cumplimiento"])
        assert exc.value.status_code == 403

    def test_sin_roles_da_403(self):
        dep = require_roles("alta_gerencia")
        with pytest.raises(HTTPException) as exc:
            _ejecutar(dep, [])
        assert exc.value.status_code == 403

    def test_sin_argumentos_solo_admin(self):
        dep = require_roles()
        assert _ejecutar(dep, ["admin"])["user_id"] == "test"
        with pytest.raises(HTTPException) as exc:
            _ejecutar(dep, ["alta_gerencia", "oficial_cumplimiento"])
        assert exc.value.status_code == 403

    def test_multiples_roles_permitidos(self):
        dep = require_roles("oficial_cumplimiento", "alta_gerencia")
        assert _ejecutar(dep, ["oficial_cumplimiento"])
        assert _ejecutar(dep, ["alta_gerencia"])
