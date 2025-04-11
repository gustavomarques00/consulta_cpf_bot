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
    response = requests.get(f"{BASE_URL}/operacaoes/operadores", headers=auth_headers)

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
    payload = {"operador_id": int(operador_id), "quantidade_dados": 50}

    response = requests.post(
        f"{BASE_URL}/operacaoes/distribuir-dados", json=payload, headers=auth_headers
    )

    assert response.status_code == 200, f"❌ Erro ao distribuir dados: {response.text}"
    assert "message" in response.json(), "❌ Resposta não contém a chave 'message'"
    assert (
        "sucesso" in response.json()["message"].lower()
    ), "❌ Mensagem não indica sucesso"


# Testa a distribuição de dados com quantidade inválida
def test_progresso_operadores(headers, chefe_token):
    """
    Testa a visualização do progresso dos Operadores.
    Verifica se a resposta contém os dados de progresso no formato esperado.
    """
    auth_headers = {**headers, "Authorization": f"Bearer {chefe_token}"}
    response = requests.get(
        f"{BASE_URL}/operacaoes/progresso-operadores", headers=auth_headers
    )

    assert (
        response.status_code == 200
    ), f"❌ Erro ao consultar progresso: {response.text}"
    data = response.json()
    assert "progresso" in data, "❌ Resposta não contém a chave 'progresso'"
    assert isinstance(data["progresso"], list), "❌ Progresso não é uma lista"

    # Verificar estrutura dos dados de progresso se houver algum operador
    if data["progresso"]:
        operador = data["progresso"][0]
        assert (
            "operador_id" in operador
        ), "❌ Dados do operador não contêm 'operador_id'"
        assert "nome" in operador, "❌ Dados do operador não contêm 'nome'"
        assert (
            "dados_distribuidos" in operador
        ), "❌ Dados do operador não contêm 'dados_distribuidos'"
        assert (
            "dados_restantes" in operador
        ), "❌ Dados do operador não contêm 'dados_restantes'"


# Verifica se os dados distribuídos e restantes são inteiros
def test_historico_distribuicao(chefe_token, base_url):
    """
    Testa o endpoint de histórico de distribuição de dados para o Chefe de Equipe.
    """
    headers = {
        "Authorization": f"Bearer {chefe_token}",
        "Content-Type": "application/json",
    }

    # Faz a requisição para o endpoint
    response = requests.get(
        f"{base_url}/operacaoes/historico-distribuicao", headers=headers
    )

    # Verifica o status da resposta
    assert (
        response.status_code == 200
    ), f"Esperado 200, mas obteve {response.status_code}. Resposta: {response.text}"

    # Verifica o conteúdo da resposta
    data = response.json()
    assert "historico" in data, "A resposta não contém o campo 'historico'"
    assert isinstance(data["historico"], list), "O campo 'historico' não é uma lista"

    # Verifica a estrutura de um item do histórico (se houver dados)
    if data["historico"]:
        item = data["historico"][0]
        assert (
            "data_distribuicao" in item
        ), "Falta o campo 'data_distribuicao' no histórico"
        assert "operador_id" in item, "Falta o campo 'operador_id' no histórico"
        assert "nome_operador" in item, "Falta o campo 'nome_operador' no histórico"
        assert (
            "dados_distribuidos" in item
        ), "Falta o campo 'dados_distribuidos' no histórico"
        assert isinstance(
            item["dados_distribuidos"], int
        ), "'dados_distribuidos' não é um inteiro"


def test_reatribuir_dados_sucesso(chefe_token, base_url):
    """
    Testa a reatribuição de dados entre dois operadores com sucesso.
    """
    headers = {
        "Authorization": f"Bearer {chefe_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "operador_origem_id": 7,  # Operador Teste
        "operador_destino_id": 8,  # Operador 2
        "quantidade_dados": 50,
    }

    response = requests.post(
        f"{base_url}/operacaoes/reatribuir-dados", json=payload, headers=headers
    )

    # Verifica o status da resposta
    assert (
        response.status_code == 200
    ), f"Esperado 200, mas obteve {response.status_code}. Resposta: {response.text}"

    # Verifica o conteúdo da resposta
    data = response.json()
    assert data["message"] == "✅ Dados reatribuídos com sucesso."
    assert data["operador_origem_id"] == payload["operador_origem_id"]
    assert data["operador_destino_id"] == payload["operador_destino_id"]
    assert data["quantidade_dados"] == payload["quantidade_dados"]


def test_reatribuir_dados_operador_origem_invalido(chefe_token, base_url):
    """
    Testa a reatribuição de dados com um operador de origem inválido.
    """
    headers = {
        "Authorization": f"Bearer {chefe_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "operador_origem_id": 999,  # Operador inválido (não associado ao chefe)
        "operador_destino_id": 8,  # Operador válido
        "quantidade_dados": 50,
    }

    response = requests.post(
        f"{base_url}/operacaoes/reatribuir-dados", json=payload, headers=headers
    )

    # Verifica o status da resposta
    assert (
        response.status_code == 403
    ), f"Esperado 403, mas obteve {response.status_code}. Resposta: {response.text}"

    # Verifica o conteúdo da resposta
    data = response.json()
    assert data["error"] == "O Operador de origem não pertence ao Chefe de Equipe"


def test_reatribuir_dados_operador_destino_invalido(chefe_token, base_url):
    """
    Testa a reatribuição de dados com um operador de destino inválido.
    """
    headers = {
        "Authorization": f"Bearer {chefe_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "operador_origem_id": 7,  # Operador válido
        "operador_destino_id": 999,  # Operador inválido (não associado ao chefe)
        "quantidade_dados": 50,
    }

    print(f"Token usado: {chefe_token}")
    print(f"Payload enviado: {payload}")

    response = requests.post(
        f"{base_url}/operacaoes/reatribuir-dados", json=payload, headers=headers
    )

    # Verifica o status da resposta
    assert (
        response.status_code == 403
    ), f"Esperado 403, mas obteve {response.status_code}. Resposta: {response.text}"

    # Verifica o conteúdo da resposta
    data = response.json()
    assert data["error"] == "O Operador de destino não pertence ao Chefe de Equipe"


def test_reatribuir_dados_quantidade_insuficiente(chefe_token, base_url):
    """
    Testa a reatribuição de dados com quantidade insuficiente no operador de origem.
    """
    headers = {
        "Authorization": f"Bearer {chefe_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "operador_origem_id": 7,  # Operador Teste
        "operador_destino_id": 8,  # Operador 2
        "quantidade_dados": 1000,  # Quantidade maior do que o disponível
    }

    response = requests.post(
        f"{base_url}/operacaoes/reatribuir-dados", json=payload, headers=headers
    )

    # Verifica o status da resposta
    assert (
        response.status_code == 400
    ), f"Esperado 400, mas obteve {response.status_code}. Resposta: {response.text}"

    # Verifica o conteúdo da resposta
    data = response.json()
    assert data["error"] == "O Operador de origem não possui dados suficientes"


def test_reatribuir_dados_quantidade_negativa(chefe_token, base_url):
    """
    Testa a reatribuição de dados com quantidade negativa.
    """
    headers = {
        "Authorization": f"Bearer {chefe_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "operador_origem_id": 7,  # Operador Teste
        "operador_destino_id": 8,  # Operador 2
        "quantidade_dados": -10,  # Quantidade negativa
    }

    response = requests.post(
        f"{base_url}/operacaoes/reatribuir-dados", json=payload, headers=headers
    )

    # Verifica o status da resposta
    assert (
        response.status_code == 400
    ), f"Esperado 400, mas obteve {response.status_code}. Resposta: {response.text}"

    # Verifica o conteúdo da resposta
    data = response.json()
    assert data["error"] == "A quantidade de dados deve ser um número positivo"


def test_notificar_operador_sucesso(chefe_token, base_url):
    headers = {
        "Authorization": f"Bearer {chefe_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "operador_id": 7,
        "mensagem": "Você recebeu novos dados para processar.",
    }

    response = requests.post(
        f"{base_url}/notificacoes/notificar-operador", json=payload, headers=headers
    )

    assert response.status_code == 200, f"Erro: {response.text}"
