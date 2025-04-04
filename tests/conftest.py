from unittest.mock import MagicMock
import requests
import pytest
from dotenv import load_dotenv
import os

# 🔄 Carrega as variáveis do .env para uso nos testes
load_dotenv()

# 🌍 URL base da API a ser testada
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")

# ================================
# FIXTURES PARA O TESTE
# ================================


@pytest.fixture(scope="module")
def base_url() -> str:
    """Retorna a URL base para os testes."""
    return os.getenv("BASE_URL", "http://127.0.0.1:5000")


@pytest.fixture(scope="module")
def headers() -> dict:
    """Cabeçalhos padrão para testes de API (Content-Type JSON)."""
    return {"Content-Type": "application/json"}


@pytest.fixture(scope="module")
def token(headers) -> str:
    """
    Gera um token de acesso válido para testes autenticados.
    Utiliza as variáveis TEST_USER_ID e TEST_USER_CARGO do .env.
    """
    user_id = os.getenv("TEST_USER_ID")
    cargo = os.getenv("TEST_USER_CARGO")

    assert user_id, "❌ TEST_USER_ID não configurado no .env"
    assert cargo, "❌ TEST_USER_CARGO não configurado no .env"

    response = requests.post(
        f"{BASE_URL}/api/generate-token",
        json={"user_id": int(user_id), "cargo": cargo},
        headers=headers,
    )
    assert response.status_code == 200, f"❌ Erro ao gerar token: {response.text}"
    return response.json()["token"]


@pytest.fixture(scope="module")
def invalid_token(headers) -> str:
    """
    Gera um token de acesso válido e o corrompe para testes de acesso com token inválido.
    """
    user_id = os.getenv("TEST_USER_ID")
    cargo = os.getenv("TEST_USER_CARGO")

    assert user_id, "❌ TEST_USER_ID não configurado no .env"
    assert cargo, "❌ TEST_USER_CARGO não configurado no .env"

    # Gera um token válido
    response = requests.post(
        f"{BASE_URL}/api/generate-token",
        json={"user_id": int(user_id), "cargo": cargo},
        headers=headers,
    )
    assert response.status_code == 200, f"❌ Erro ao gerar token: {response.text}"

    # Corrompe o token para torná-lo inválido
    invalid_token = (
        response.json()["token"][:10] + "invalid_part"
    )  # Simplesmente corrompe o token
    return invalid_token


@pytest.fixture(scope="module")
def refresh_token(headers) -> str:
    """
    Gera um refresh_token válido para testes de renovação de sessão.
    """
    user_id = os.getenv("TEST_USER_ID")
    cargo = os.getenv("TEST_USER_CARGO")

    response = requests.post(
        f"{BASE_URL}/api/generate-token",
        json={"user_id": int(user_id), "cargo": cargo},
        headers=headers,
    )
    assert (
        response.status_code == 200
    ), f"❌ Erro ao gerar refresh_token: {response.text}"
    return response.json()["refresh_token"]


# ================================
# MOCK PARA GOOGLE SHEETS
# ================================
@pytest.fixture
def mock_sheet_checker() -> MagicMock:
    """
    Retorna um mock que simula a aba 'Checker' do Google Sheets,
    usada para armazenar a fila de CPFs a serem processados.
    """
    mock = MagicMock()
    # Definindo comportamentos simulados para os métodos
    mock.get_all_values.return_value = [["CPF"], ["12345678901"], ["10987654321"]]
    mock.delete_rows.return_value = None
    return mock
