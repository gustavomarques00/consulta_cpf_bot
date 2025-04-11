import pytest
import requests
import os
from tests.conftest import BASE_URL

# ==== TESTES PÚBLICOS ====


def test_get_plans(headers):
    """Testa se a rota pública retorna uma lista de planos."""
    response = requests.get(f"{BASE_URL}/servicos/plans", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list) and len(data) > 0


# ==== TESTES AUTENTICADOS ====


def test_get_user_plan(token, headers):
    """Testa se usuário autenticado consegue consultar seu plano usando JWT."""
    auth_headers = {
        **headers,
        "Authorization": f"Bearer {token['token']}",
    }  # Use token['token']
    response = requests.get(f"{BASE_URL}/servicos/user-plans", headers=auth_headers)
    assert (
        response.status_code == 200
    ), f"Erro ao acessar /servicos/user-plans: {response.text}"
    data = response.json()
    assert "id" in data and "nome" in data

# ==== TESTES DE ERRO COM TOKEN ====


def test_protected_route_without_token():
    """Acesso sem token deve retornar erro 401."""
    response = requests.get(f"{BASE_URL}/servicos/user-plans")
    assert response.status_code == 401


def test_protected_route_with_invalid_token():
    """Acesso com token inválido deve retornar erro 401."""
    headers = {"Authorization": "Bearer token_invalido"}
    response = requests.get(f"{BASE_URL}/servicos/user-plans", headers=headers)
    assert response.status_code == 401
    assert "inválido" in response.json().get("error", "").lower()


# ==== TESTES DE REFRESH TOKEN ====


def test_revoke_refresh_token(headers):
    """Revoga um refresh_token gerado dinamicamente via rota ADMIN."""
    # Gera tokens
    response = requests.post(
        f"{BASE_URL}/admin/generate-token",
        json={"user_id": 4, "cargo": "ADM"},
        headers=headers,
    )
    assert response.status_code == 200
    refresh_token = response.json()["refresh_token"]
    access_token = response.json()["token"]

    admin_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {"refresh_token": refresh_token}  # Corrigido para usar "refresh_token"
    revoke_resp = requests.post(
        f"{BASE_URL}/admin/revoke-refresh-token",
        json=payload,
        headers=admin_headers,
    )
    assert (
        revoke_resp.status_code == 200
    ), f"Erro ao revogar refresh_token: {revoke_resp.text}"
    assert "revogado" in revoke_resp.json().get("message", "").lower()


def test_refresh_token_renova_token(refresh_token):
    """Usa um refresh_token da fixture para gerar novo token."""
    headers = {"Refresh-Token": refresh_token}
    response = requests.post(f"{BASE_URL}/admin/refresh-token", headers=headers)
    assert response.status_code == 200
    assert "token" in response.json()


# ==== TESTES DE REVOGAÇÃO ====


def test_revoke_token(token, headers):
    """Revoga o próprio token via /admin/revoke-token."""
    auth_headers = {**headers, "Authorization": f"Bearer {token['token']}"}
    payload = {"token": token["token"]}
    response = requests.post(
        f"{BASE_URL}/admin/revoke-token", json=payload, headers=auth_headers
    )
    assert response.status_code == 200, f"Erro ao revogar token: {response.text}"
    assert "revogado" in response.json().get("message", "").lower()


# ==== TESTE DE LISTAGEM DE REFRESH TOKENS ADMIN ====


def test_list_refresh_tokens_paginated(headers):
    """Testa paginação e filtros da rota de tokens do admin."""
    response = requests.post(
        f"{BASE_URL}/admin/generate-token",
        json={"user_id": 4, "cargo": "ADM"},
        headers=headers,
    )
    token = response.json().get("token")
    assert token

    headers_auth = {"Authorization": f"Bearer {token}"}
    params = {"page": 1, "limit": 5, "email": "admin", "revogado": "false"}
    response = requests.get(
        f"{BASE_URL}/admin/refresh-tokens", headers=headers_auth, params=params
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data and isinstance(data["data"], list)
