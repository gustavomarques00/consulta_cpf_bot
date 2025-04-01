import pytest
import requests
from dotenv import load_dotenv
import os
from utils.token import generate_tokens  # ajuste o path se estiver diferente

# ================================
# CONFIGURAÇÃO INICIAL E FIXTURES
# ================================

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")


@pytest.fixture(scope="module")
def headers():
    """
    Retorna headers padrão para requisições JSON.
    """
    return {"Content-Type": "application/json"}


@pytest.fixture(scope="module")
def refresh_token(headers):
    """
    Gera um refresh_token válido para testes a partir das variáveis do .env
    """
    user_id = os.getenv("TEST_USER_ID")
    cargo = os.getenv("TEST_USER_CARGO")

    assert user_id, "Variável de ambiente TEST_USER_ID não configurada"
    assert cargo, "Variável de ambiente TEST_USER_CARGO não configurada"

    response = requests.post(
        f"{BASE_URL}/api/generate-token",
        json={"user_id": user_id, "cargo": cargo},
        headers=headers,
    )
    assert response.status_code == 200, f"Falha ao gerar refresh_token: {response.text}"
    return response.json().get("refresh_token")


@pytest.fixture(scope="module")
def token(headers):
    """
    Gera um token de acesso (access_token) válido para o usuário ADM.
    """
    user_id = os.getenv("TEST_USER_ID")
    cargo = os.getenv("TEST_USER_CARGO")

    assert user_id, "Variável de ambiente TEST_USER_ID não configurada"
    assert cargo, "Variável de ambiente TEST_USER_CARGO não configurada"

    payload = {"user_id": user_id, "cargo": cargo}
    response = requests.post(
        f"{BASE_URL}/api/generate-token", json=payload, headers=headers
    )
    assert response.status_code == 200, f"Falha ao gerar token: {response.text}"
    return response.json().get("token")


# ===================
# TESTES DE ROTAS API
# ===================


def test_get_plans(headers):
    """
    GET /api/plans
    Testa se a rota pública retorna uma lista de planos válidos.
    """
    response = requests.get(f"{BASE_URL}/api/plans", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list) and len(data) > 0


def test_get_user_plan(token):
    """
    GET /api/user-plans
    Testa se um usuário autenticado consegue consultar seu plano com sucesso.
    """
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/user-plans", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data and "nome" in data


def test_super_admin_access(token):
    """
    GET /api/superadmin/test
    Testa se um usuário com cargo ADM acessa rota exclusiva do superadmin.
    """
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/superadmin/test", headers=headers)
    assert response.status_code == 200
    assert "Super Admin" in response.json().get("message", "")


def test_protected_route_without_token():
    """
    GET /api/user-plans
    Tenta acessar sem token e espera erro 401.
    """
    response = requests.get(f"{BASE_URL}/api/user-plans")
    assert response.status_code == 401
    assert "Token" in response.json().get("error", "")


def test_protected_route_with_invalid_token():
    """
    GET /api/user-plans com token inválido
    Espera resposta 401 com mensagem de token inválido.
    """
    headers = {"Authorization": "Bearer token_invalido_aqui"}
    response = requests.get(f"{BASE_URL}/api/user-plans", headers=headers)
    assert response.status_code == 401
    assert "inválido" in response.json().get("error", "").lower()


def test_refresh_token(headers):
    """
    POST /api/refresh-token
    Gera manualmente um refresh_token e testa renovação do token.
    """
    response = requests.post(
        f"{BASE_URL}/api/generate-token",
        json={"user_id": 4, "cargo": "ADM"},
        headers=headers,
    )
    assert response.status_code == 200
    refresh_token = response.json().get("refresh_token")
    assert refresh_token

    refresh_headers = {"Refresh-Token": refresh_token}
    refresh_resp = requests.post(
        f"{BASE_URL}/api/refresh-token", headers=refresh_headers
    )
    assert refresh_resp.status_code == 200
    assert "token" in refresh_resp.json()


def test_refresh_token_renova_token(refresh_token):
    """
    POST /api/refresh-token
    Usa um refresh_token válido (via fixture) para renovar o token.
    """
    headers = {"Refresh-Token": refresh_token}
    response = requests.post(f"{BASE_URL}/api/refresh-token", headers=headers)
    assert response.status_code == 200
    assert "token" in response.json()


def test_revoke_token(token):
    """
    POST /api/revoke-token
    Revoga um token de acesso (access_token) válido.
    """
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"token": token}

    response = requests.post(
        f"{BASE_URL}/api/revoke-token", json=payload, headers=headers
    )
    assert response.status_code == 200
    assert "revogado" in response.json().get("message", "").lower()


def test_revoke_refresh_token(headers):
    """
    POST /api/admin/revoke-refresh-token
    Revoga um refresh_token gerado dinamicamente via rota ADMIN.
    """
    # Gera tokens
    response = requests.post(
        f"{BASE_URL}/api/generate-token",
        json={"user_id": 4, "cargo": "ADM"},
        headers=headers,
    )
    assert response.status_code == 200, f"Erro ao gerar tokens: {response.text}"
    refresh_token = response.json()["refresh_token"]
    access_token = response.json()["token"]

    # Define os headers de autenticação
    admin_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Define o payload para revogação
    payload = {"refresh_token": refresh_token}  # Corrigido para definir o payload

    # Faz a requisição para revogar o refresh_token
    revoke_resp = requests.post(
        f"{BASE_URL}/api/admin/revoke-refresh-token",
        json=payload,
        headers=admin_headers,
    )
    assert (
        revoke_resp.status_code == 200
    ), f"Erro ao revogar refresh_token: {revoke_resp.text}"
    assert "revogado" in revoke_resp.json().get("message", "").lower()


def test_list_refresh_tokens_paginated(headers):
    """
    GET /api/admin/refresh-tokens
    Testa listagem paginada de refresh tokens com filtros por e-mail e status de revogação.
    """
    response = requests.post(
        f"{BASE_URL}/api/generate-token",
        json={"user_id": 4, "cargo": "ADM"},
        headers=headers,
    )
    token = response.json().get("token")
    assert token

    headers_auth = {"Authorization": f"Bearer {token}"}
    params = {"page": 1, "limit": 5, "email": "admin", "revogado": "false"}
    response = requests.get(
        f"{BASE_URL}/api/admin/refresh-tokens", headers=headers_auth, params=params
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)
