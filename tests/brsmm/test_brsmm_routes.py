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
    # Passo 1: pegar ID do primeiro serviço válido
    services = requests.get(f"{BASE_URL}/api/brsmm/services", headers=headers).json()
    assert services and isinstance(services, list)
    service_id = services[0]["service"]

    # Passo 2: criar pedido
    payload = {"link": "https://example.com", "service_id": service_id, "quantity": 100}
    resp = requests.post(f"{BASE_URL}/api/brsmm/order", json=payload, headers=headers)
    assert resp.status_code in [200, 400]  # 400 se limite do serviço for maior

    if resp.status_code == 200:
        order_id = resp.json().get("order")
        assert order_id

        # Passo 3: consultar status
        status_resp = requests.get(
            f"{BASE_URL}/api/brsmm/status/{order_id}", headers=headers
        )
        assert status_resp.status_code == 200
        assert "status" in status_resp.json()
