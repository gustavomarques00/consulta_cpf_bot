import pytest
import requests
import os

from tests.conftest import BASE_URL

# ========================
# TESTES DE ROTAS ADMIN
# ========================


def test_revoke_refresh_token(headers, token):
    """
    🔐 POST /admin/revoke-refresh-token
    """
    refresh_token = token["refresh_token"]
    access_token = token["token"]

    admin_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {"refresh_token": refresh_token}

    response = requests.post(
        f"{BASE_URL}/admin/revoke-refresh-token",
        json=payload,
        headers=admin_headers,
    )

    assert response.status_code == 200, f"❌ Erro ao revogar token: {response.text}"
    assert "revogado" in response.json().get("message", "").lower()


def test_list_refresh_tokens_paginated(headers, token):
    """
    📄 GET /admin/refresh-tokens
    """
    access_token = token["token"]

    admin_headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "page": 1,
        "limit": 5,
        "email": "admin",
        "revogado": "false",
    }

    response = requests.get(
        f"{BASE_URL}/admin/refresh-tokens", headers=admin_headers, params=params
    )

    assert response.status_code == 200, f"❌ Falha ao buscar tokens: {response.text}"
    data = response.json()
    assert "data" in data, "❌ 'data' não encontrado na resposta"
    assert isinstance(data["data"], list), "❌ 'data' não é uma lista"
