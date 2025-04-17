import pytest
from backend.services.brsmm_service import BrsmmService

# Instância do BrsmmService
brsmm_service = BrsmmService()


def test_brsmm_services():
    """
    Testa o método get_services do BrsmmService.
    """
    services = brsmm_service.get_services()
    assert isinstance(services, list), "❌ O retorno de get_services não é uma lista"
    assert (
        "service" in services[0]
    ), "❌ O campo 'service' não foi encontrado no retorno"


def test_brsmm_balance():
    """
    Testa o método get_balance do BrsmmService.
    """
    balance = brsmm_service.get_balance()
    assert "balance" in balance, "❌ O campo 'balance' não foi encontrado no retorno"


def test_brsmm_order_and_status():
    """
    🔁 Testa o método add_order e get_order_status do BrsmmService.
    """
    service_id = 171
    test_url = "https://apretailer.com.br/click/67d4bfd92bfa815c42685e06/185510/351953/subaccount"
    quantidade = 88

    # Criação do pedido
    order_response = brsmm_service.add_order(
        link=test_url, service_id=service_id, quantity=quantidade
    )
    assert (
        "order" in order_response
    ), "❌ O campo 'order' não foi retornado ao criar o pedido"

    order_id = order_response["order"]

    # Consulta do status do pedido
    status_response = brsmm_service.get_order_status(order_id=order_id)
    assert (
        "status" in status_response
    ), "❌ O campo 'status' não foi encontrado no retorno do status do pedido"
