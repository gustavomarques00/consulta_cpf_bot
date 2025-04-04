# tests/test_token.py

# Importa as bibliotecas necessárias
import datetime
import pytest
import jwt
from utils import token as token_utils  # Importa o módulo de utilitários de token


# Testa a estrutura do token gerado
def test_generate_token_structure():
    user_id = 123  # ID do usuário
    cargo = "Operador"  # Cargo do usuário
    token = token_utils.generate_token(user_id, cargo)  # Gera o token

    # Decodifica o token sem validar a expiração
    decoded = jwt.decode(
        token, token_utils.JWT_SECRET, algorithms=[token_utils.JWT_ALGORITHM]
    )

    # Verifica se os campos esperados estão presentes e corretos
    assert decoded["user_id"] == user_id
    assert decoded["cargo"] == cargo
    assert decoded["type"] == "access"
    assert "exp" in decoded  # Verifica se o campo de expiração está presente


# Testa a criação de um token de atualização (refresh token)
def test_create_refresh_token():
    user_id = 123  # ID do usuário
    token = token_utils.create_refresh_token(user_id)  # Gera o refresh token

    # Decodifica o token gerado
    decoded = jwt.decode(
        token, token_utils.JWT_SECRET, algorithms=[token_utils.JWT_ALGORITHM]
    )

    # Verifica se os campos esperados estão presentes e corretos
    assert decoded["user_id"] == user_id
    assert decoded["type"] == "refresh"


# Testa se ambos os tokens (access e refresh) são gerados
def test_generate_tokens_both_present():
    result = token_utils.generate_tokens(1, "Operador")  # Gera os tokens
    assert "access_token" in result  # Verifica se o token de acesso está presente
    assert "refresh_token" in result  # Verifica se o refresh token está presente


# Testa a decodificação de um token válido
def test_decode_valid_token():
    token = token_utils.generate_token(1, "ADM")  # Gera um token válido
    decoded = token_utils.decode_token(token)  # Decodifica o token

    # Verifica se os campos esperados estão presentes e corretos
    assert decoded is not None
    assert decoded["user_id"] == 1
    assert decoded["cargo"] == "ADM"


# Testa a decodificação de um token inválido
def test_decode_invalid_token():
    invalid_token = "invalid.token.structure"  # Token inválido
    result = token_utils.decode_token(invalid_token)  # Tenta decodificar o token
    assert result is None  # O resultado deve ser None para tokens inválidos


# Testa a decodificação de um token expirado
def test_decode_expired_token():
    expired_token = token_utils.generate_expired_token(
        123, "Operador"
    )  # Gera um token expirado
    # Decodifica o token sem verificar a expiração
    expired_payload = jwt.decode(
        expired_token,
        "secretdoapp",
        algorithms=["HS256"],
        options={"verify_exp": False},
    )

    # Verifique se o payload contém a chave 'user_id' e 'cargo'
    assert "user_id" in expired_payload
    assert "cargo" in expired_payload
