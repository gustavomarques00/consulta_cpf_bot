from venv import logger
import pytest
from services.trafego_service import TrafegoService
from services.brsmm_service import BrsmmService
from core.db import get_db_connection

# Instancia os serviços
trafego_service = TrafegoService()
brsmm_service = BrsmmService()


def test_enviar_pedido(verificar_erro_resposta):
    """
    Testa o envio de tráfego via serviço e verifica se foi registrado no banco.
    """

    # Sincroniza os serviços disponíveis com o banco de dados
    brsmm_service.sync_services_to_db()

    # Dados fixos para o teste
    user_id = 1
    service_id = 171
    test_url = "https://apretailer.com.br/click/valid-url"
    quantidade = 88

    # Envia o pedido
    response = trafego_service.enviar_pedido(user_id, service_id, test_url, quantidade)

    # Verifica se ocorreu algum erro na resposta usando a fixture
    verificar_erro_resposta(response)

    # Validações adicionais
    assert "order_id" in response, "❌ O retorno não contém 'order_id'."
    assert isinstance(response["order_id"], int), "❌ 'order_id' não é um inteiro."
    assert response["message"].startswith("✅"), "❌ Mensagem inesperada no retorno."


def test_enviar_trafego():
    """
    Testa o envio de tráfego via serviço.
    """

    # Sincroniza os serviços disponíveis com o banco de dados
    brsmm_service.sync_services_to_db()

    # Dados do pedido
    user_id = 1
    service_id = 171
    test_url = "https://apretailer.com.br/click/67d4bfd92bfa815c42685e06/185510/351953/subaccount"
    quantidade = 88

    # Envia o pedido
    response = trafego_service.enviar_pedido(user_id, service_id, test_url, quantidade)
    logger.info(f"Resposta do envio de pedido: {response}")

    # Verifica se o pedido foi enviado com sucesso ou se ocorreu um erro
    if "error" in response:
        pytest.fail(f"Erro ao enviar pedido: {response['error']}")

    assert "order_id" in response, "❌ O retorno não contém 'order_id'."
    assert isinstance(response["order_id"], int), "❌ 'order_id' não é um inteiro."
    assert response["message"].startswith("✅"), "❌ Mensagem inesperada no retorno."


def test_enviar_trafego_com_id_usuario():
    """
    Testa o envio de tráfego via serviço e verifica se o ID do usuário foi registrado corretamente no banco.
    """

    # Sincroniza os serviços disponíveis com o banco de dados
    brsmm_service.sync_services_to_db()

    # Dados fixos para o teste
    user_id = 1  # ID do usuário de teste
    service_id = 171
    test_url = "https://apretailer.com.br/click/67c140362bfa8136ea48f2f9/185510/349334/subaccount"
    quantidade = 88

    # Envia o pedido
    response = trafego_service.enviar_pedido(user_id, service_id, test_url, quantidade)

    # Verifica se o pedido foi enviado com sucesso ou se ocorreu um erro
    if "error" in response:
        pytest.fail(f"Erro ao enviar pedido: {response['error']}")

    assert "order_id" in response, "❌ O retorno não contém 'order_id'."
    assert isinstance(response["order_id"], int), "❌ 'order_id' não é um inteiro."
    assert response["message"].startswith("✅"), "❌ Mensagem inesperada no retorno."


def test_meus_pedidos_sem_filtros():
    """
    Testa a consulta de pedidos do usuário sem filtros.
    """
    user_id = 1  # ID do usuário de teste

    # Consulta os pedidos
    response = trafego_service.consultar_meus_pedidos(user_id)

    # Validações na resposta
    assert "data" in response, "❌ O retorno não contém 'data'."
    assert isinstance(response["data"], list), "❌ 'data' não é uma lista."
    assert "total_pages" in response, "❌ O retorno não contém 'total_pages'."
    assert "page" in response, "❌ O retorno não contém 'page'."
    assert "limit" in response, "❌ O retorno não contém 'limit'."


def test_meus_pedidos_com_filtro_status():
    """
    Testa a consulta de pedidos do usuário com filtro de status.
    """
    user_id = 1  # ID do usuário de teste
    status = "sucesso"

    # Consulta os pedidos com filtro de status
    response = trafego_service.consultar_meus_pedidos(user_id, status=status)

    # Validações na resposta
    for pedido in response["data"]:
        assert pedido["status"] == status, "❌ 'status' do pedido não corresponde."


def test_status_pedido():
    """
    Testa a consulta de status de um pedido específico.
    """
    user_id = 1
    order_id = 999001  # ID do pedido para teste
    service_id = 171
    test_url = "https://apretailer.com.br/click/valid-url"
    quantidade = 88
    preco_total = 74.8
    status = "Em andamento"

    # Insere manualmente um pedido na tabela para o teste
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO trafego_pedidos (
            id, user_id, url, quantidade, preco_total, brsmm_order_id, status, criado_em, service_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s)
        ON DUPLICATE KEY UPDATE status = VALUES(status)
        """,
        (
            order_id,
            user_id,
            test_url,
            quantidade,
            preco_total,
            order_id,
            status,
            service_id,
        ),
    )
    conn.commit()
    cursor.close()
    conn.close()

    # Consulta o status do pedido
    response = trafego_service.consultar_status_pedido(order_id, user_id)

    # Validações na resposta
    assert "status" in response, "❌ O retorno não contém 'status'."
    assert response["status"] == status, "❌ Status do pedido não corresponde."
    assert "brsmm_order_id" in response, "❌ O retorno não contém 'brsmm_order_id'."
    assert (
        response["brsmm_order_id"] == order_id
    ), "❌ O 'brsmm_order_id' não corresponde."
    assert response["quantidade"] == quantidade, "❌ A 'quantidade' não corresponde."
    assert response["preco_total"] == preco_total, "❌ O 'preco_total' não corresponde."
