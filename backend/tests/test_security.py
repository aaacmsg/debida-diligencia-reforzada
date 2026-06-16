import pytest
from datetime import timedelta, datetime
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_token,
)


class TestPasswordHashing:
    def test_hash_es_diferente_al_plaintext(self):
        password = "MiPassword123!"
        hashed = get_password_hash(password)
        assert hashed != password

    def test_verify_password_correcto(self):
        password = "MiPassword123!"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrecto(self):
        password = "MiPassword123!"
        wrong = "OtraPassword456!"
        hashed = get_password_hash(password)
        assert verify_password(wrong, hashed) is False

    def test_hashes_son_distintos_misma_password(self):
        password = "MiPassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2

    def test_password_vacia(self):
        hashed = get_password_hash("")
        assert verify_password("", hashed) is True

    def test_password_con_caracteres_especiales(self):
        password = "P@$$w0rd!ñññ"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True


class TestJWTTokens:
    def test_create_access_token_retorna_string(self):
        token = create_access_token({"sub": "testuser", "roles": ["admin"]})
        assert isinstance(token, str)
        assert len(token) > 20

    def test_decode_token_valido(self):
        token = create_access_token({"sub": "testuser", "roles": ["admin"]})
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["roles"] == ["admin"]

    def test_decode_token_con_roles(self):
        token = create_access_token({"sub": "oficial", "roles": ["oficial_cumplimiento", "admin"]})
        payload = decode_token(token)
        assert payload["roles"] == ["oficial_cumplimiento", "admin"]

    def test_token_expirado_retorna_none(self):
        token = create_access_token(
            {"sub": "testuser"},
            expires_delta=timedelta(seconds=-1)
        )
        payload = decode_token(token)
        assert payload is None

    def test_token_invalido_retorna_none(self):
        payload = decode_token("token.invalido.aqui")
        assert payload is None

    def test_token_modificado_retorna_none(self):
        token = create_access_token({"sub": "testuser"})
        partes = token.split(".")
        token_modificado = partes[0] + "." + partes[1] + ".firma_invalida"
        payload = decode_token(token_modificado)
        assert payload is None

    def test_token_contiene_exp(self):
        token = create_access_token({"sub": "testuser"})
        payload = decode_token(token)
        assert "exp" in payload

    def test_token_exp_no_ha_expirado(self):
        import time as _time
        token = create_access_token(
            {"sub": "testuser"},
            expires_delta=timedelta(hours=1)
        )
        payload = decode_token(token)
        exp = payload["exp"]
        now = _time.time()
        assert exp > now
