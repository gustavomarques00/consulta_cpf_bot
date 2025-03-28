import pytest
import requests
from dotenv import load_dotenv
import os

# ========================================
# CONFIGURAÇÃO INICIAL E FIXTURES GLOBAIS
# ========================================

load_dotenv()
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")

@pytest.fixture
def headers():
    """Retorna headers padrão para requisições JSON."""
    return {"Content-Type": "application/json"}


# =============================
# TESTES DE TOKEN E AUTORIZAÇÃO ADMIN
# =============================

def gerar_tokens_adm(headers):
    """
    Gera access_token e refresh_token válidos para o cargo ADM.
    Útil para evitar repetição de código e garantir tokens atualizados.
    """
    user_id = os.getenv("TEST_USER_ID")
    cargo = os.getenv("TEST_USER_CARGO")

    assert user_id and cargo, "Variáveis TEST_USER_ID e TEST_USER_CARGO devem estar configuradas no .env"

    payload = {"user_id": int(user_id), "cargo": cargo}
    resp = requests.post(f"{BASE_URL}/api/generate-token", json=payload, headers=headers)
    assert resp.status_code == 200, "Erro ao gerar tokens de teste"
    tokens = resp.json()
    assert "token" in tokens and "refresh_token" in tokens, "Tokens não retornados corretamente"
    return tokens


def test_revoke_refresh_token(headers):
    """
    Gera e revoga um refresh_token via rota protegida ADMIN.
    Verifica se a revogação ocorre com sucesso e a mensagem correta é retornada.
    """
    tokens = gerar_tokens_adm(headers)
    refresh_token = tokens["refresh_token"]
    access_token = tokens["token"]

    admin_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {"refresh_token": refresh_token}  # Certifique-se de que o backend espera "refresh_token"
    revoke_resp = requests.post(f"{BASE_URL}/api/admin/revoke-refresh-token", json=payload, headers=admin_headers)

    assert revoke_resp.status_code == 200, f"Erro ao revogar refresh_token: {revoke_resp.text}"
    assert "revogado" in revoke_resp.json().get("message", "").lower(), "Mensagem de revogação não encontrada"


def test_list_refresh_tokens_paginated(headers):
    """
    Lista refresh tokens com filtros de paginação e revogação.
    Garante que a resposta contenha uma estrutura paginada válida.
    """
    tokens = gerar_tokens_adm(headers)
    access_token = tokens["token"]

    headers_auth = {"Authorization": f"Bearer {access_token}"}
    params = {
        "page": 1,
        "limit": 5,
        "email": "admin",         # Altere aqui se necessário
        "revogado": "false"
    }

    resp = requests.get(f"{BASE_URL}/api/admin/refresh-tokens", headers=headers_auth, params=params)

    assert resp.status_code == 200, f"Falha ao buscar tokens: {resp.text}"
    data = resp.json()
    assert "data" in data, "Resposta não contém 'data'"
    assert isinstance(data["data"], list), "'data' não é uma lista"
