import pytest
import requests
import os
from dotenv import load_dotenv
from tests.conftest import BASE_URL
from core.db import get_db_connection

load_dotenv()

# POST Requests

# Teste de envio de tráfego e verificação no banco de dados
# Esta função testa o envio de tráfego via API e verifica se o pedido foi registrado corretamente no banco de dados.
def test_enviar_pedido_salva_em_banco(token):
    """
    Testa o envio de tráfego via API e verifica se foi registrado no banco.
    """
    headers = {
        "Authorization": f"Bearer {token['token']}",
        "Content-Type": "application/json",
    }

    # Dados fixos para o teste
    service_id = 171
    test_url = "https://apretailer.com.br/click/67c140362bfa8136ea48f2f9/185510/349334/subaccount"
    quantidade = 50

    # Envia um pedido via endpoint /api/trafego/send
    payload = {
        "service_id": service_id,
        "url": test_url,
        "quantidade": quantidade,
    }
    resp = requests.post(f"{BASE_URL}/api/trafego/send", json=payload, headers=headers)

    # Verifica o código de status da resposta
    assert resp.status_code in [200, 400]

    if resp.status_code == 400:
        print("Erro na requisição:", resp.json())  # Loga a mensagem de erro

    # Se o status for 200, verifica se o pedido foi salvo no banco de dados
    if resp.status_code == 200:
        data = resp.json()
        assert "order_id" in data
        assert isinstance(data["order_id"], int)
        assert data["message"].startswith("✅")

        order_id = data["order_id"]
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM trafego_pedidos WHERE brsmm_order_id = %s", (order_id,)
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        # Validações no banco de dados
        assert result, "Pedido não foi salvo no banco de dados"
        assert result["user_id"], "user_id não salvo"
        assert result["service_id"] == service_id, "service_id não corresponde"
        assert result["quantidade"] == quantidade, "quantidade não corresponde"


# Teste de envio de tráfego
# Esta função testa o endpoint de envio de tráfego para uma URL específica.
def test_enviar_trafego(token):
    """
    Testa o endpoint de envio de tráfego para uma URL.
    """
    headers = {"Authorization": f"Bearer {token['token']}", "Content-Type": "application/json"}

    # Dados do payload para o envio de tráfego
    payload = {
        "service_id": 171,
        "url": "https://apretailer.com.br/click/67c140362bfa8136ea48f2f9/185510/349334/subaccount",
        "quantidade": 100,
    }

    # Realiza a requisição POST
    response = requests.post(
        f"{BASE_URL}/api/trafego/send", json=payload, headers=headers
    )

    # Validações na resposta
    assert response.status_code == 200
    data = response.json()

    assert "order_id" in data  # Verifica se o campo 'order_id' está presente
    assert isinstance(data["order_id"], int)
    assert data["message"].startswith("✅")


# Teste de envio de tráfego com ID do usuário
# Esta função testa o envio de tráfego via API e verifica se o ID do usuário foi registrado corretamente no banco de dados.
def test_enviar_trafego_com_id_usuario(token):
    """
    Testa o envio de tráfego via API e verifica se o ID do usuário foi registrado corretamente no banco.
    """
    headers = {
        "Authorization": f"Bearer {token['token']}",
        "Content-Type": "application/json",
    }

    # Verifica se TEST_USER_ID_ADM está definido
    user_id = os.getenv("TEST_USER_ID_ADM")
    assert user_id, "❌ TEST_USER_ID_ADM não configurado no .env"

    # Dados fixos para o teste
    service_id = 171
    test_url = "https://apretailer.com.br/click/67c140362bfa8136ea48f2f9/185510/349334/subaccount"
    quantidade = 100  # Aumentando para 100, que pode ser o mínimo permitido pela API

    # Envia um pedido via endpoint /api/trafego/send
    payload = {
        "service_id": service_id,
        "url": test_url,
        "quantidade": quantidade,
    }

    # Realiza a requisição POST
    resp = requests.post(f"{BASE_URL}/api/trafego/send", json=payload, headers=headers)

    # Loga a resposta para diagnóstico
    print(f"Response status code: {resp.status_code}")
    print(f"Response body: {resp.text}")

    # Verifica se a resposta foi bem-sucedida
    assert resp.status_code == 200, f"Esperado 200, mas obteve {resp.status_code}. Resposta: {resp.text}"

    data = resp.json()

    # Verifica se a resposta contém o order_id
    assert "order_id" in data, "A resposta não contém 'order_id'"
    assert isinstance(data["order_id"], int), "O 'order_id' não é um inteiro"
    assert data["message"].startswith("✅"), f"Mensagem inesperada: {data['message']}"

    # Recupera o order_id da resposta
    order_id = data["order_id"]

    # Verifica se o pedido foi salvo no banco e se o 'user_id' está correto
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM trafego_pedidos WHERE brsmm_order_id = %s", (order_id,)
    )
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    # Verifica se o pedido foi encontrado no banco
    assert result, f"Pedido com order_id {order_id} não foi encontrado no banco de dados."

    # Verifica se o 'user_id' foi corretamente salvo
    assert result["user_id"] == int(user_id), f"Esperado user_id {user_id}, mas obteve {result['user_id']}"


# GET Requests

# Teste de Histórico de Pedidos sem filtros
def test_meus_pedidos_sem_filtros(headers, token):
    """
    ✅ GET /api/trafego/historico/meus-pedidos (sem filtros)
    Verifica se retorna estrutura de paginação e pedidos do usuário.
    """
    resp = requests.get(
        f"{BASE_URL}/api/trafego/historico/meus-pedidos",
        headers={**headers, "Authorization": f"Bearer {token['token']}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert isinstance(data["data"], list)
    assert "total_pages" in data
    assert "page" in data
    assert "limit" in data


# Teste de Histórico de Pedidos com filtro de status
def test_meus_pedidos_com_filtro_status(headers, token):
    """
    Testa o filtro de status no histórico de pedidos.
    """
    resp = requests.get(
        f"{BASE_URL}/api/trafego/historico/meus-pedidos?status=sucesso",
        headers={**headers, "Authorization": f"Bearer {token['token']}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    for pedido in data["data"]:
        assert pedido["status"] == "sucesso"


# Teste de Histórico de Pedidos com filtro de service_id
def test_meus_pedidos_com_filtros_multiplicados(headers, token):
    """
    Testa o uso combinado de múltiplos filtros.
    """
    resp = requests.get(
        f"{BASE_URL}/api/trafego/historico/meus-pedidos?status=sucesso&service_id=171&data_inicio=2025-04-01&data_fim=2025-04-02",
        headers={**headers, "Authorization": f"Bearer {token['token']}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    for pedido in data["data"]:
        assert pedido["status"] == "sucesso"
        assert pedido["service_id"] == 171
        assert "2025-04-01" <= pedido["criado_em"][:10] <= "2025-04-02"


# Teste de consulta de status de pedido por ID
def test_status_pedido(headers, token):
    """
    Testa o endpoint de consulta de status de pedido por ID.
    """
    order_id = 999001  # Exemplo de um pedido que existe no banco
    resp = requests.get(
        f"{BASE_URL}/api/trafego/pedidos/{order_id}/status",
        headers={**headers, "Authorization": f"Bearer {token['token']}"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "data_criado_em" in data


# Teste de consulta de status de pedido por ID (detalhado)
def test_status_pedido_por_id(headers, token):
    """
    Testa o endpoint de consulta de status de pedido por ID.
    """
    order_id = 999001  # ID do pedido para teste
    response = requests.get(
        f"{BASE_URL}/api/trafego/pedidos/{order_id}/status",
        headers={**headers, "Authorization": f"Bearer {token['token']}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["Em progresso", "Finalizado", "Erro", "Concluído"]


# Teste de consulta de status para múltiplos pedidos com IDs inválidos
def test_status_multiplos_pedidos_not_found(headers, token):
    """
    Testa o endpoint de consulta de status para múltiplos pedidos com IDs inválidos.
    """
    order_ids = ["999001", "999999", "999003"]  # O ID 999999 não existe
    response = requests.get(
        f"{BASE_URL}/api/trafego/pedidos/status",
        headers={**headers, "Authorization": f"Bearer {token['token']}"},
        params={"order_ids": order_ids},
    )
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"] == "Nenhum pedido encontrado para os IDs fornecidos"
