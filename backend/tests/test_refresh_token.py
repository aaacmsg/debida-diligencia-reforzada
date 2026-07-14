"""Tests de refresh tokens JWT - issue #97."""
import asyncio

import pytest
from fastapi import HTTPException
from jose import jwt

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)


class TestRefreshToken:

    def test_refresh_token_tiene_type_refresh(self):
        token = create_refresh_token({"sub": "admin", "roles": ["admin"]})
        payload = decode_token(token)
        assert payload is not None
        assert payload["type"] == "refresh"
        assert payload["sub"] == "admin"

    def test_access_token_no_tiene_type_refresh(self):
        token = create_access_token({"sub": "admin", "roles": ["admin"]})
        payload = decode_token(token)
        assert payload is not None
        assert payload.get("type") != "refresh"

    def test_refresh_expira_en_dias_configurados(self):
        token = create_refresh_token({"sub": "admin"})
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        access = create_access_token({"sub": "admin"})
        access_payload = jwt.decode(access, settings.secret_key, algorithms=[settings.algorithm])
        # El refresh debe durar bastante mas que el access (7 dias vs 60 min)
        assert payload["exp"] > access_payload["exp"]

    def test_refresh_token_no_sirve_como_access(self):
        """Un refresh token usado como Bearer debe dar 401."""
        token = create_refresh_token({"sub": "admin", "roles": ["admin"]})
        with pytest.raises(HTTPException) as exc:
            asyncio.run(get_current_user(token=token, db=None))
        assert exc.value.status_code == 401

    def test_access_token_valido_pasa(self):
        token = create_access_token({"sub": "admin", "roles": ["admin"]})
        user = asyncio.run(get_current_user(token=token, db=None))
        assert user["user_id"] == "admin"
        assert user["roles"] == ["admin"]
