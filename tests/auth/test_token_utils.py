# tests/test_token.py

import pytest
import jwt
from utils import token as token_utils


def test_generate_token_structure():
    user_id = 123
    cargo = "Operador"
    token = token_utils.generate_token(user_id, cargo)

    # Decodifica sem validar expiração
    decoded = jwt.decode(
        token, token_utils.JWT_SECRET, algorithms=[token_utils.JWT_ALGORITHM]
    )

    assert decoded["user_id"] == user_id
    assert decoded["cargo"] == cargo
    assert decoded["type"] == "access"
    assert "exp" in decoded


def test_create_refresh_token():
    user_id = 123
    token = token_utils.create_refresh_token(user_id)

    decoded = jwt.decode(
        token, token_utils.JWT_SECRET, algorithms=[token_utils.JWT_ALGORITHM]
    )

    assert decoded["user_id"] == user_id
    assert decoded["type"] == "refresh"


def test_generate_tokens_both_present():
    result = token_utils.generate_tokens(1, "Operador")
    assert "access_token" in result
    assert "refresh_token" in result


def test_decode_valid_token():
    token = token_utils.generate_token(1, "ADM")
    decoded = token_utils.decode_token(token)

    assert decoded is not None
    assert decoded["user_id"] == 1
    assert decoded["cargo"] == "ADM"


def test_decode_invalid_token():
    invalid_token = "invalid.token.structure"
    result = token_utils.decode_token(invalid_token)
    assert result is None
