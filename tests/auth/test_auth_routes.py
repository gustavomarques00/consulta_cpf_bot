import pytest
import requests
from dotenv import load_dotenv
import os
from core.db import get_db_connection

# ========================================
# CONFIGURAÇÃO INICIAL E FIXTURES GLOBAIS
# ========================================

# Carrega as variáveis de ambiente do .env
load_dotenv()
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM refresh_tokens;")
    conn.commit()
    cursor.close()
    conn.close()


@pytest.fixture
def headers():
    """
    Headers padrão para requisições JSON.
    """
    return {"Content-Type": "application/json"}


# ========================================
# TESTES DE GERAÇÃO, RENOVAÇÃO E REVOGAÇÃO
# ========================================


def test_generate_and_refresh_token(headers):
    """
    🔄 Gera um refresh_token e o utiliza para obter novo access_token.

    Fluxo testado:
    - Chama /api/generate-token para gerar tokens
    - Usa o refresh_token na rota /api/refresh-token
    - Verifica se um novo token é retornado corretamente
    """
    # Geração dos tokens
    resp = requests.post(
        f"{BASE_URL}/api/generate-token",
        json={"user_id": 4, "cargo": "ADM"},
        headers=headers,
    )
    assert resp.status_code == 200, f"Erro ao gerar token: {resp.text}"
    tokens = resp.json()

    assert "token" in tokens and "refresh_token" in tokens, "Tokens não retornados"

    # Renovação usando refresh_token
    refresh_headers = {"Refresh-Token": tokens["refresh_token"]}
    refresh_resp = requests.post(
        f"{BASE_URL}/api/refresh-token", headers=refresh_headers
    )

    assert (
        refresh_resp.status_code == 200
    ), f"Erro ao renovar token: {refresh_resp.text}"
    assert "token" in refresh_resp.json(), "Novo token não retornado"


def test_revoke_token(headers):
    """
    ❌ Testa a revogação manual de um access_token pela rota /api/revoke-token.

    Verifica:
    - Se o token pode ser revogado com sucesso
    - Se a mensagem de confirmação é retornada corretamente
    """
    # Geração de token
    resp = requests.post(
        f"{BASE_URL}/api/generate-token",
        json={"user_id": 4, "cargo": "ADM"},
        headers=headers,
    )
    access_token = resp.json().get("token")

    # Envio para revogação
    auth_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {"token": access_token}

    revoke_resp = requests.post(
        f"{BASE_URL}/api/revoke-token", json=payload, headers=auth_headers
    )

    assert revoke_resp.status_code == 200
    assert "revogado" in revoke_resp.json().get("message", "").lower()


def test_revoke_refresh_token(headers):
    """
    🔐 Revoga um refresh_token autenticado pela rota ADMIN.

    Valida:
    - Geração de tokens válidos
    - Envio do refresh_token para revogação
    - Confirmação da revogação com status 200 e mensagem apropriada
    """
    # Geração de tokens
    response = requests.post(
        f"{BASE_URL}/api/generate-token",
        json={"user_id": 4, "cargo": "ADM"},
        headers=headers,
    )
    assert response.status_code == 200, f"Erro ao gerar token: {response.text}"
    tokens = response.json()
    refresh_token = tokens["refresh_token"]
    access_token = tokens["token"]

    # Headers de autenticação ADM
    admin_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Define o payload para revogação
    payload = {"refresh_token": refresh_token}  # Ajuste aqui se necessário

    # Requisição para revogar o refresh_token
    revoke_resp = requests.post(
        f"{BASE_URL}/api/admin/revoke-refresh-token",
        json=payload,
        headers=admin_headers,
    )
    assert revoke_resp.status_code == 200, f"Erro ao revogar token: {revoke_resp.text}"
    assert "revogado" in revoke_resp.json().get("message", "").lower()


def test_list_refresh_tokens_paginated(headers):
    """
    📄 Lista todos os refresh tokens com paginação e filtros aplicados.

    Valida:
    - Geração de token de administrador
    - Acesso à rota protegida /admin/refresh-tokens
    - Retorno com chave 'data' e estrutura de lista paginada
    """
    # Geração de token ADM
    resp = requests.post(
        f"{BASE_URL}/api/generate-token",
        json={"user_id": 4, "cargo": "ADM"},
        headers=headers,
    )
    assert resp.status_code == 200, f"Erro ao gerar token: {resp.text}"
    tokens = resp.json()
    access_token = tokens["token"]

    # Filtros de listagem
    headers_auth = {"Authorization": f"Bearer {access_token}"}
    params = {"page": 1, "limit": 5, "email": "admin", "revogado": "false"}

    # Requisição para listagem de tokens
    resp = requests.get(
        f"{BASE_URL}/api/admin/refresh-tokens", headers=headers_auth, params=params
    )
    assert resp.status_code == 200, f"Falha ao buscar tokens: {resp.text}"
    assert "data" in resp.json(), "Resposta não contém 'data'"
    assert isinstance(resp.json()["data"], list), "Dados retornados não são uma lista"
