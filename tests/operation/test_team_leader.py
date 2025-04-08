import pytest
import requests
import os

from tests.conftest import BASE_URL

def test_listar_operadores(headers, chefe_token):
    """
    Testa a listagem de operadores associados ao Chefe de Equipe.
    Verifica se a resposta contém a lista de operadores no formato esperado.
    """
    auth_headers = {**headers, "Authorization": f"Bearer {chefe_token}"}
    response = requests.get(f"{BASE_URL}/api/chefe/operadores", headers=auth_headers)
    
    assert response.status_code == 200, f"❌ Erro ao listar operadores: {response.text}"
    data = response.json()
    assert "operadores" in data, "❌ Resposta não contém a chave 'operadores'"
    assert isinstance(data["operadores"], list), "❌ Operadores não é uma lista"

def test_distribuir_dados(headers, chefe_token):
    """
    Testa a distribuição de dados para um Operador.
    Verifica se a API confirma o sucesso da operação.
    """
    operador_id = os.getenv("TEST_USER_ID_OPERADOR")  # ID do operador vindo do .env
    
    auth_headers = {**headers, "Authorization": f"Bearer {chefe_token}"}
    payload = {
        "operador_id": int(operador_id),
        "quantidade_dados": 50
    }
    
    response = requests.post(
        f"{BASE_URL}/api/chefe/distribuir-dados", 
        json=payload, 
        headers=auth_headers
    )
    
    assert response.status_code == 200, f"❌ Erro ao distribuir dados: {response.text}"
    assert "message" in response.json(), "❌ Resposta não contém a chave 'message'"
    assert "sucesso" in response.json()["message"].lower(), "❌ Mensagem não indica sucesso"

def test_progresso_operadores(headers, chefe_token):
    """
    Testa a visualização do progresso dos Operadores.
    Verifica se a resposta contém os dados de progresso no formato esperado.
    """
    auth_headers = {**headers, "Authorization": f"Bearer {chefe_token}"}
    response = requests.get(f"{BASE_URL}/api/chefe/progresso-operadores", headers=auth_headers)
    
    assert response.status_code == 200, f"❌ Erro ao consultar progresso: {response.text}"
    data = response.json()
    assert "progresso" in data, "❌ Resposta não contém a chave 'progresso'"
    assert isinstance(data["progresso"], list), "❌ Progresso não é uma lista"
    
    # Verificar estrutura dos dados de progresso se houver algum operador
    if data["progresso"]:
        operador = data["progresso"][0]
        assert "operador_id" in operador, "❌ Dados do operador não contêm 'operador_id'"
        assert "nome" in operador, "❌ Dados do operador não contêm 'nome'"
        assert "dados_distribuidos" in operador, "❌ Dados do operador não contêm 'dados_distribuidos'"
        assert "dados_restantes" in operador, "❌ Dados do operador não contêm 'dados_restantes'"