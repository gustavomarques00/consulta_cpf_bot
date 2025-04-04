import pytest
import jwt
from utils import token as token_utils


# ========================
# FIXTURES E FUNÇÕES GLOBAIS
# ========================


@pytest.fixture
def user_data():
    """
    Fixture para fornecer dados de usuário comuns para os testes.
    """
    return {"user_id": 123, "cargo": "Operador"}


# ========================
# TESTES DE TOKEN
# ========================


def test_generate_token_structure(user_data):
    """
    Testa se a estrutura do token gerado está correta.
    Verifica:
    - O token contém os dados do usuário
    - O tipo de token é "access"
    - O campo "exp" está presente no token
    """
    token = token_utils.generate_token(user_data["user_id"], user_data["cargo"])

    # Decodifica sem validar expiração
    decoded = jwt.decode(
        token, token_utils.JWT_SECRET, algorithms=[token_utils.JWT_ALGORITHM]
    )

    assert decoded["user_id"] == user_data["user_id"]
    assert decoded["cargo"] == user_data["cargo"]
    assert decoded["type"] == "access"
    assert "exp" in decoded


def test_create_refresh_token(user_data):
    """
    Testa se o refresh token é criado corretamente.
    Verifica:
    - O refresh token contém os dados corretos
    - O tipo de token é "refresh"
    """
    token = token_utils.create_refresh_token(user_data["user_id"])

    decoded = jwt.decode(
        token, token_utils.JWT_SECRET, algorithms=[token_utils.JWT_ALGORITHM]
    )

    assert decoded["user_id"] == user_data["user_id"]
    assert decoded["type"] == "refresh"


def test_generate_tokens_both_present(user_data):
    """
    Testa se tanto o access_token quanto o refresh_token são gerados corretamente.
    Verifica:
    - Se ambos os tokens estão presentes no resultado
    """
    result = token_utils.generate_tokens(user_data["user_id"], user_data["cargo"])

    assert "access_token" in result
    assert "refresh_token" in result


def test_decode_valid_token(user_data):
    """
    Testa se a decodificação de um token válido retorna os dados corretos.
    Verifica:
    - Se o token decodificado contém o user_id e cargo corretos
    """
    token = token_utils.generate_token(user_data["user_id"], user_data["cargo"])
    decoded = token_utils.decode_token(token)

    assert decoded is not None
    assert decoded["user_id"] == user_data["user_id"]
    assert decoded["cargo"] == user_data["cargo"]


def test_decode_invalid_token():
    """
    Testa se a decodificação de um token inválido retorna None.
    Verifica:
    - Se um token inválido não retorna dados
    """
    invalid_token = "invalid.token.structure"
    result = token_utils.decode_token(invalid_token)

    assert result is None
