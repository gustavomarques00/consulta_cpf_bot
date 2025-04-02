# tests/conftest.py

import pytest
import requests
from dotenv import load_dotenv
import os

# 🔄 Carrega as variáveis do .env para uso nos testes
load_dotenv()

# 🌍 URL base da API a ser testada
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")


@pytest.fixture(scope="module")
def headers():
    """
    ✅ Cabeçalhos padrão para testes de API (Content-Type JSON).
    """
    return {"Content-Type": "application/json"}


@pytest.fixture(scope="module")
def token(headers):
    """
    🔐 Gera um token de acesso válido para testes autenticados.
    Utiliza as variáveis TEST_USER_ID e TEST_USER_CARGO do .env
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
def refresh_token(headers):
    """
    🔁 Gera um refresh_token válido para testes de renovação de sessão.
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
