import pytest
import requests
from dotenv import load_dotenv
import os

load_dotenv()
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")


@pytest.fixture(scope="module")
def headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


def test_meus_pedidos_sem_filtros(headers):
    """
    ✅ GET /api/trafego/historico/meus-pedidos (sem filtros)
    Verifica se retorna estrutura de paginação e pedidos do usuário.
    """
    resp = requests.get(f"{BASE_URL}/api/trafego/historico/meus-pedidos", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    assert "data" in data
    assert isinstance(data["data"], list)
    assert "total_pages" in data
    assert "page" in data
    assert "limit" in data


def test_meus_pedidos_com_filtro_status(headers):
    """
    ✅ GET /api/trafego/historico/meus-pedidos?status=Concluído
    Verifica se o filtro de status funciona corretamente.
    """
    resp = requests.get(
        f"{BASE_URL}/api/trafego/historico/meus-pedidos?status=Concluído",
        headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    for pedido in data["data"]:
        assert pedido["status"] == "Concluído"


def test_meus_pedidos_filtro_service_id(headers):
    """
    ✅ GET /api/trafego/historico/meus-pedidos?service_id=171
    Filtra os pedidos feitos com o service_id 171.
    """
    resp = requests.get(
        f"{BASE_URL}/api/trafego/historico/meus-pedidos?service_id=171",
        headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    for pedido in data["data"]:
        assert pedido["service_id"] == 171


def test_meus_pedidos_filtro_data(headers):
    """
    ✅ GET /api/trafego/historico/meus-pedidos?data_inicio=2025-04-01&data_fim=2025-04-02
    Filtra por intervalo de datas.
    """
    resp = requests.get(
        f"{BASE_URL}/api/trafego/historico/meus-pedidos?data_inicio=2025-04-01&data_fim=2025-04-02",
        headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert isinstance(data["data"], list)


def test_status_pedido(headers):
    """
    Testa o endpoint de consulta de status de pedido por ID.
    """
    order_id = 999001  # Exemplo de um pedido que existe no banco
    resp = requests.get(f"{BASE_URL}/api/trafego/pedidos/{order_id}/status", headers=headers)
    
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "data_criado_em" in data


def test_status_multiplos_pedidos(headers):
    """
    Testa o endpoint de consulta de status para múltiplos pedidos.
    """
    order_ids = [999001, 999002, 999003]  # IDs dos pedidos existentes
    resp = requests.get(f"{BASE_URL}/api/trafego/pedidos/status", headers=headers, params={"order_ids": order_ids})
    
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == len(order_ids)


def test_status_pedido_por_id(headers):
    """
    Testa o endpoint de consulta de status de pedido por ID.
    """
    order_id = 999001  # ID do pedido para teste
    response = requests.get(f"{BASE_URL}/api/trafego/pedidos/{order_id}/status", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["Em progresso", "Finalizado", "Erro", "Concluído"]


def test_status_multiplos_pedidos_success(headers):
    """
    Testa o endpoint de consulta de status para múltiplos pedidos.
    """
    order_ids = ["999001", "999002", "999003"]  # IDs válidos de pedidos para o teste
    response = requests.get(
        f"{BASE_URL}/api/trafego/pedidos/status", headers=headers, params={"order_ids": order_ids}
    )
    assert response.status_code == 200  # Espera-se que o status seja 200, pois os IDs existem
    data = response.json()
    assert len(data) == len(order_ids)  # Espera-se que o número de pedidos na resposta seja igual ao enviado
    for pedido in data:
        assert "order_id" in pedido
        assert "status" in pedido



def test_status_multiplos_pedidos_not_found(headers):
    """
    Testa o endpoint de consulta de status para múltiplos pedidos com IDs inválidos.
    """
    order_ids = ["999001", "999999", "999003"]  # O ID 999999 não existe
    response = requests.get(
        f"{BASE_URL}/api/trafego/pedidos/status", headers=headers, params={"order_ids": order_ids}
    )
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"] == "Nenhum pedido encontrado para os IDs fornecidos"