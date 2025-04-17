import pytest
import jwt  # type: ignore
from core.config import Config
from services.token_service import TokenService
from tests.conftest import (
    JWT_SECRET,
    JWT_ALGORITHM,
)

# Instancia o serviço de token com as configurações corretas
token_service = TokenService(jwt_secret=JWT_SECRET, jwt_algorithm=JWT_ALGORITHM)

def test_generate_token_structure(chefe_token):
    """
    Testa se a estrutura do token gerado está correta.
    Verifica:
    - O token contém os dados do usuário
    - O tipo de token é "access"
    - O campo "exp" está presente no token
    """
    # Decodifica sem validar expiração
    decoded = jwt.decode(
        chefe_token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM]
    )

    assert decoded["user_id"] == 1
    assert decoded["cargo"] == "CHEFE DE EQUIPE"
    assert decoded["type"] == "access"
    assert "exp" in decoded


def test_create_refresh_token(refresh_token):
    """
    Testa se o refresh token é criado corretamente.
    Verifica:
    - O refresh token contém os dados corretos
    - O tipo de token é "refresh"
    """
    decoded = jwt.decode(
        refresh_token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM]
    )

    assert decoded["user_id"] == 1
    assert decoded["type"] == "refresh"


def test_generate_tokens_both_present(chefe_token, refresh_token):
    """
    Testa se tanto o access_token quanto o refresh_token são gerados corretamente.
    Verifica:
    - Se ambos os tokens estão presentes no resultado
    """
    assert chefe_token is not None
    assert refresh_token is not None


def test_decode_valid_token(chefe_token):
    """
    Testa se a decodificação de um token válido retorna os dados corretos.
    Verifica:
    - Se o token decodificado contém o user_id e cargo corretos
    """
    decoded = jwt.decode(
        chefe_token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM]
    )

    assert decoded is not None
    assert decoded["user_id"] == 1
    assert decoded["cargo"] == "CHEFE DE EQUIPE"


def test_decode_invalid_token(invalid_token):
    """
    Testa se a decodificação de um token inválido retorna None.
    Verifica:
    - Se um token inválido não retorna dados
    """
    with pytest.raises(jwt.exceptions.DecodeError, match="Not enough segments"):
        jwt.decode(invalid_token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])


def test_blacklisted_token(chefe_token):
    """
    Testa se um token na blacklist é identificado corretamente.
    """
    # Revoga o token
    token_service.revogar_access_token(chefe_token)

    # Verifica se o token está na blacklist
    is_blacklisted = token_service.is_token_blacklisted(chefe_token)
    assert is_blacklisted is True
