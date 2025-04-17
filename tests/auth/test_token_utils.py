import datetime
import pytest
import jwt  # type: ignore
from backend.services.token_service import TokenService

# Configurações para o TokenService
JWT_SECRET = "secretdoapp"
JWT_ALGORITHM = "HS256"
token_service = TokenService(jwt_secret=JWT_SECRET, jwt_algorithm=JWT_ALGORITHM)


# Testa a estrutura do token gerado
def test_generate_token_structure():
    user_id = 123  # ID do usuário
    cargo = "Operador"  # Cargo do usuário
    token = token_service.generate_access_token(user_id, cargo)  # Gera o token

    # Decodifica o token sem validar a expiração
    decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

    # Verifica se os campos esperados estão presentes e corretos
    assert decoded["user_id"] == user_id
    assert decoded["cargo"] == cargo
    assert decoded["type"] == "access"
    assert "exp" in decoded  # Verifica se o campo de expiração está presente


# Testa a criação de um token de atualização (refresh token)
def test_create_refresh_token():
    user_id = 123  # ID do usuário
    token = token_service.generate_refresh_token(user_id)  # Gera o refresh token

    # Decodifica o token gerado
    decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

    # Verifica se os campos esperados estão presentes e corretos
    assert decoded["user_id"] == user_id
    assert decoded["type"] == "refresh"


# Testa se ambos os tokens (access e refresh) são gerados
def test_generate_tokens_both_present():
    result = token_service.generate_and_store_token(1, "Operador")  # Gera os tokens
    assert "access_token" in result  # Verifica se o token de acesso está presente
    assert "refresh_token" in result  # Verifica se o refresh token está presente


# Testa a decodificação de um token válido
def test_decode_valid_token():
    token = token_service.generate_access_token(1, "ADM")  # Gera um token válido
    decoded = token_service.decode_token(token)  # Decodifica o token

    # Verifica se os campos esperados estão presentes e corretos
    assert decoded is not None
    assert decoded["user_id"] == 1
    assert decoded["cargo"] == "ADM"


# Testa a decodificação de um token inválido
def test_decode_invalid_token():
    invalid_token = "invalid.token.structure"  # Token inválido
    with pytest.raises(ValueError, match="Token inválido!"):
        token_service.decode_token(invalid_token)  # Tenta decodificar o token


# Testa a decodificação de um token expirado
def test_decode_expired_token():
    # Gera um token expirado
    expired_token = jwt.encode(
        {
            "user_id": 123,
            "cargo": "Operador",
            "type": "access",
            "exp": datetime.datetime.now() - datetime.timedelta(seconds=1),
        },
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )

    # Tenta decodificar o token e verifica se a exceção é levantada
    with pytest.raises(ValueError, match="Token expirado!"):
        token_service.decode_token(expired_token)
