import pytest
import requests

# Base URL do backend Flask
BASE_URL = "http://127.0.0.1:5000"


@pytest.fixture(scope="module")
def headers():
    """
    Headers padrão para requisições JSON.
    """
    return {"Content-Type": "application/json"}


@pytest.fixture(scope="module")
def token(headers):
    """
    Gera um token válido para o usuário ADM.
    Retorna o token em string para ser reutilizado em testes protegidos.
    """
    payload = {"user_id": 4, "cargo": "ADM"}
    response = requests.post(f"{BASE_URL}/api/generate-token", json=payload, headers=headers)
    assert response.status_code == 200, "Falha ao gerar token"

    token_value = response.json().get("token")
    assert token_value, "Token não retornado na resposta"
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
    assert "id" in data and "nome" in data, "Plano deve conter ID e nome"


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
