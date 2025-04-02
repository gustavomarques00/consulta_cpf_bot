import pytest  # type: ignore
import requests
import os
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")


@pytest.fixture
def headers():
    user_id = os.getenv("TEST_USER_ID")
    cargo = os.getenv("TEST_USER_CARGO")
    assert (
        user_id and cargo
    ), "Variáveis TEST_USER_ID e TEST_USER_CARGO não configuradas"

    resp = requests.post(
        f"{BASE_URL}/api/generate-token", json={"user_id": user_id, "cargo": cargo}
    )
    assert resp.status_code == 200
    token = resp.json().get("token")

    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def test_brsmm_services(headers):
    resp = requests.get(f"{BASE_URL}/api/brsmm/services", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert "service" in data[0]


def test_brsmm_balance(headers):
    resp = requests.get(f"{BASE_URL}/api/brsmm/balance", headers=headers)
    assert resp.status_code == 200
    assert "balance" in resp.json()


def test_brsmm_order_and_status(headers):
    """
    🔁 Testa envio de pedido fixo e consulta de status com service_id 171.
    """
    service_id = 171
    test_url = "https://apretailer.com.br/click/67c140362bfa8136ea48f2f9/185510/349334/subaccount"
    quantidade = 50

    payload = {"link": test_url, "service_id": service_id, "quantity": quantidade}
    resp = requests.post(f"{BASE_URL}/api/brsmm/order", json=payload, headers=headers)
    assert resp.status_code in [200, 400]

    if resp.status_code == 200:
        order_id = resp.json().get("order")
        assert order_id, "Pedido não retornou order_id"

        # Consulta status
        status_resp = requests.get(
            f"{BASE_URL}/api/brsmm/status/{order_id}", headers=headers
        )
        assert status_resp.status_code == 200
        assert "status" in status_resp.json()