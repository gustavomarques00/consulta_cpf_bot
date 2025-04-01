import pytest
import requests
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")


# ========================
# FIXTURE GLOBAL: HEADERS
# ========================
@pytest.fixture(scope="module")
def headers():
    return {"Content-Type": "application/json"}


# ========================
# FUNÇÃO DE SUPORTE
# ========================
def gerar_tokens_adm(headers):
    """
    Gera access_token e refresh_token válidos para o cargo ADM.
    """
    user_id = os.getenv("TEST_USER_ID")
    cargo = os.getenv("TEST_USER_CARGO")

    assert (
        user_id and cargo
    ), "⚠️ TEST_USER_ID e TEST_USER_CARGO devem estar definidos no .env"

    payload = {"user_id": int(user_id), "cargo": cargo}
    response = requests.post(
        f"{BASE_URL}/api/generate-token", json=payload, headers=headers
    )

    assert response.status_code == 200, "❌ Falha ao gerar tokens de teste"
    tokens = response.json()

    assert (
        "token" in tokens and "refresh_token" in tokens
    ), "❌ Tokens não retornados corretamente"
    return tokens


# ========================
# TESTES DE ROTAS ADMIN
# ========================


def test_revoke_refresh_token(headers):
    """
    🔐 POST /api/admin/revoke-refresh-token

    Testa a revogação de um refresh_token via rota protegida para administradores.
    """
    tokens = gerar_tokens_adm(headers)
    refresh_token = tokens["refresh_token"]
    access_token = tokens["token"]

    admin_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {"refresh_token": refresh_token}

    response = requests.post(
        f"{BASE_URL}/api/admin/revoke-refresh-token",
        json=payload,
        headers=admin_headers,
    )

    assert response.status_code == 200, f"❌ Erro ao revogar token: {response.text}"
    assert "revogado" in response.json().get("message", "").lower()


def test_list_refresh_tokens_paginated(headers):
    """
    📄 GET /api/admin/refresh-tokens

    Lista refresh tokens com filtros de paginação e revogação.
    Verifica se a estrutura de resposta está correta.
    """
    tokens = gerar_tokens_adm(headers)
    access_token = tokens["token"]

    admin_headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "page": 1,
        "limit": 5,
        "email": "admin",  # ajuste conforme seu teste
        "revogado": "false",
    }

    response = requests.get(
        f"{BASE_URL}/api/admin/refresh-tokens", headers=admin_headers, params=params
    )

    assert response.status_code == 200, f"❌ Falha ao buscar tokens: {response.text}"
    data = response.json()
    assert "data" in data, "❌ 'data' não encontrado na resposta"
    assert isinstance(data["data"], list), "❌ 'data' não é uma lista"
