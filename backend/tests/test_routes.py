import pytest
import requests
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Base URL do backend Flask
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")

@pytest.fixture(scope="module")
def headers():
    """
    Headers padrão para requisições JSON.
    """
    return {"Content-Type": "application/json"}


@pytest.fixture(scope="module")
def refresh_token(headers):
    """
    Gera um refresh_token válido para testes.
    """
    user_id = os.getenv("TEST_USER_ID")
    cargo = os.getenv("TEST_USER_CARGO")

    assert user_id, "Variável de ambiente TEST_USER_ID não configurada"
    assert cargo, "Variável de ambiente TEST_USER_CARGO não configurada"

    response = requests.post(
        f"{BASE_URL}/api/generate-token",
        json={"user_id": user_id, "cargo": cargo},
        headers=headers
    )
    assert response.status_code == 200, f"Falha ao gerar refresh_token: {response.text}"
    token = response.json().get("refresh_token")
    assert token, f"refresh_token não retornado: {response.json()}"
    return token


@pytest.fixture(scope="module")
def token(headers):
    """
    Gera um token válido para o usuário ADM.
    Retorna o token em string para ser reutilizado em testes protegidos.
    """
    user_id = os.getenv("TEST_USER_ID")
    cargo = os.getenv("TEST_USER_CARGO")

    assert user_id, "Variável de ambiente TEST_USER_ID não configurada"
    assert cargo, "Variável de ambiente TEST_USER_CARGO não configurada"

    payload = {"user_id": user_id, "cargo": cargo}
    response = requests.post(f"{BASE_URL}/api/generate-token", json=payload, headers=headers)
    assert response.status_code == 200, f"Falha ao gerar token: {response.text}"

    token_value = response.json().get("token")
    assert token_value, f"Token não retornado na resposta: {response.json()}"
    return token_value


def test_get_plans(headers):
    """
    Testa a rota pública /api/plans que retorna todos os planos.
    Espera-se uma lista com pelo menos 1 plano.
    """
    response = requests.get(f"{BASE_URL}/api/plans", headers=headers)
    assert response.status_code == 200, "Falha ao listar planos"
    data = response.json()
    assert isinstance(data, list), "Resposta deve ser uma lista"
    assert len(data) > 0, "Deve haver ao menos 1 plano disponível"


def test_get_user_plan(token):
    """
    Testa a rota protegida /api/user-plans com um token válido.
    Espera-se os dados do plano associado ao usuário autenticado.
    """
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/user-plans", headers=headers)
    assert response.status_code == 200, "Falha ao acessar plano do usuário"
    data = response.json()
    assert "id" in data and "name" in data, "Plano deve conter ID e nome"


def test_super_admin_access(token):
    """
    Testa a rota exclusiva para usuários com cargo ADM.
    Deve retornar sucesso e mensagem personalizada.
    """
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/superadmin/test", headers=headers)
    assert response.status_code == 200, "Acesso negado ao superadmin"
    assert "Super Admin" in response.json().get("message", ""), "Mensagem incorreta"


# ----------- Casos de ERRO / validação negativa -----------

def test_protected_route_without_token():
    """
    Tenta acessar uma rota protegida sem enviar token.
    Deve retornar erro 401.
    """
    response = requests.get(f"{BASE_URL}/api/user-plans")
    assert response.status_code == 401
    assert "Token" in response.json().get("error", "")


def test_protected_route_with_invalid_token():
    """
    Tenta acessar uma rota protegida com token inválido.
    Deve retornar erro 401 de token inválido.
    """
    headers = {"Authorization": "Bearer token_invalido_aqui"}
    response = requests.get(f"{BASE_URL}/api/user-plans", headers=headers)
    assert response.status_code == 401
    assert "inválido" in response.json().get("error", "").lower()

def test_refresh_token(headers):
    """
    Testa a rota de renovação de token (refresh-token).
    1. Gera um refresh_token válido
    2. Usa o refresh_token para obter um novo access_token
    """
    # Gerar manualmente um refresh_token
    response = requests.post(
        f"{BASE_URL}/api/generate-token",
        json={"user_id": 4, "cargo": "ADM"},
        headers=headers
    )
    assert response.status_code == 200, "Falha ao gerar refresh_token"

    # Extraindo token de access + refresh
    refresh_token = response.json().get("refresh_token")
    assert refresh_token, "refresh_token não retornado"

    # Usar o refresh_token para renovar
    refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
    refresh_resp = requests.post(f"{BASE_URL}/api/refresh-token", headers=refresh_headers)
    assert refresh_resp.status_code == 200, "Falha ao renovar token"
    data = refresh_resp.json()
    assert "token" in data, "Novo token não retornado"

def test_refresh_token_renova_token(refresh_token):
    """
    Usa um refresh_token para renovar e obter um novo access_token.
    As credenciais são carregadas de variáveis de ambiente para evitar hardcoded credentials.
    """
    # Carregar credenciais de variáveis de ambiente
    user_id = os.getenv("TEST_USER_ID")
    cargo = os.getenv("TEST_USER_CARGO")

    assert user_id, "4"
    assert cargo, "ADM"

    # Headers para a requisição
    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = requests.post(f"{BASE_URL}/api/refresh-token", headers=headers)
    
    # Verificar a resposta
    assert response.status_code == 200, f"Falha ao renovar token: {response.text}"
    data = response.json()
    assert "token" in data, f"Novo token não retornado: {data}"

def test_revoke_token(token):
    """
    Testa a revogação manual de um token pelo super admin.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {"token": token}

    response = requests.post(f"{BASE_URL}/api/revoke-token", json=payload, headers=headers)
    assert response.status_code == 200, "Falha ao revogar token"
    assert "revogado" in response.json().get("message", "").lower(), "Mensagem de revogação não encontrada"

def test_revoke_refresh_token(refresh_token, token):
    """
    Testa a revogação de um refresh_token via rota admin.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {"token": refresh_token}
    response = requests.post(f"{BASE_URL}/api/admin/revoke-refresh-token", json=payload, headers=headers)
    assert response.status_code == 200, "Falha ao revogar refresh_token"
    assert "revogado" in response.json().get("message", "").lower(), "Mensagem de revogação não encontrada"

def test_list_refresh_tokens_paginated(token):
    """
    Testa listagem de refresh tokens com filtros e paginação.
    """
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "page": 1,
        "limit": 5,
        "email": "admin",
        "revogado": "false"
    }
    response = requests.get(f"{BASE_URL}/api/admin/refresh-tokens", headers=headers, params=params)
    assert response.status_code == 200, f"Falha ao listar refresh tokens: {response.text}"
    data = response.json()
    assert "data" in data, f"Resposta não contém dados: {data}"
    assert isinstance(data["data"], list), "Dados retornados não são uma lista"




