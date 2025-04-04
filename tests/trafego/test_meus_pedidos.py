import requests
import os

# URL base da API a ser testada
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")


# Teste de Histórico de Pedidos sem filtros
def test_meus_pedidos_sem_filtros(headers, token):
    """
    ✅ GET /api/trafego/historico/meus-pedidos (sem filtros)
    Verifica se retorna estrutura de paginação e pedidos do usuário.
    """
    resp = requests.get(
        f"{BASE_URL}/api/trafego/historico/meus-pedidos",
        headers={**headers, "Authorization": f"Bearer {token}"},
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
        headers={**headers, "Authorization": f"Bearer {token}"},
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
        headers={**headers, "Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    for pedido in data["data"]:
        assert pedido["status"] == "sucesso"
        assert pedido["service_id"] == 171
        assert "2025-04-01" <= pedido["criado_em"][:10] <= "2025-04-02"



# Teste de Histórico de Pedidos com filtro de service_id
def test_meus_pedidos_filtro_service_id(headers, token):
    """
    ✅ GET /api/trafego/historico/meus-pedidos?service_id=171
    Filtra os pedidos feitos com o service_id 171.
    """
    resp = requests.get(
        f"{BASE_URL}/api/trafego/historico/meus-pedidos?service_id=171",
        headers={**headers, "Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    for pedido in data["data"]:
        assert pedido["service_id"] == 171


# Teste de Histórico de Pedidos com filtro de intervalo de datas
def test_meus_pedidos_filtro_data(headers, token):
    """
    ✅ GET /api/trafego/historico/meus-pedidos?data_inicio=2025-04-01&data_fim=2025-04-02
    Filtra por intervalo de datas.
    """
    resp = requests.get(
        f"{BASE_URL}/api/trafego/historico/meus-pedidos?data_inicio=2025-04-01&data_fim=2025-04-02",
        headers={**headers, "Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert isinstance(data["data"], list)


# Teste de consulta de status de pedido por ID
def test_status_pedido(headers, token):
    """
    Testa o endpoint de consulta de status de pedido por ID.
    """
    order_id = 999001  # Exemplo de um pedido que existe no banco
    resp = requests.get(
        f"{BASE_URL}/api/trafego/pedidos/{order_id}/status",
        headers={**headers, "Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "data_criado_em" in data


# Teste de consulta de status para múltiplos pedidos
def test_status_multiplos_pedidos(headers, token):
    """
    Testa o endpoint de consulta de status para múltiplos pedidos.
    """
    order_ids = ["999001", "999002", "999003"]  # IDs válidos de pedidos para o teste
    response = requests.get(
        f"{BASE_URL}/api/trafego/pedidos/status",
        headers={**headers, "Authorization": f"Bearer {token}"},
        params={"order_ids": order_ids},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(order_ids)
    for pedido in data:
        assert "order_id" in pedido
        assert "status" in pedido



# Teste de consulta de status de pedido por ID (detalhado)
def test_status_pedido_por_id(headers, token):
    """
    Testa o endpoint de consulta de status de pedido por ID.
    """
    order_id = 999001  # ID do pedido para teste
    response = requests.get(
        f"{BASE_URL}/api/trafego/pedidos/{order_id}/status",
        headers={**headers, "Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["Em progresso", "Finalizado", "Erro", "Concluído"]


# Teste de consulta de status para múltiplos pedidos (sucesso)
def test_status_multiplos_pedidos_success(headers, token):
    """
    Testa o endpoint de consulta de status para múltiplos pedidos.
    """
    order_ids = ["999001", "999002", "999003"]  # IDs válidos de pedidos para o teste
    response = requests.get(
        f"{BASE_URL}/api/trafego/pedidos/status",
        headers={**headers, "Authorization": f"Bearer {token}"},
        params={"order_ids": order_ids},
    )
    assert (
        response.status_code == 200
    )  # Espera-se que o status seja 200, pois os IDs existem
    data = response.json()
    assert len(data) == len(
        order_ids
    )  # Espera-se que o número de pedidos na resposta seja igual ao enviado
    for pedido in data:
        assert "order_id" in pedido
        assert "status" in pedido


# Teste de consulta de status para múltiplos pedidos com IDs inválidos
def test_status_multiplos_pedidos_not_found(headers, token):
    """
    Testa o endpoint de consulta de status para múltiplos pedidos com IDs inválidos.
    """
    order_ids = ["999001", "999999", "999003"]  # O ID 999999 não existe
    response = requests.get(
        f"{BASE_URL}/api/trafego/pedidos/status",
        headers={**headers, "Authorization": f"Bearer {token}"},
        params={"order_ids": order_ids},
    )
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"] == "Nenhum pedido encontrado para os IDs fornecidos"
