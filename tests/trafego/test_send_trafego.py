import pytest
import requests
from dotenv import load_dotenv
import os

load_dotenv()
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")

@pytest.fixture
def token():
    user_id = os.getenv("TEST_USER_ID")
    cargo = os.getenv("TEST_USER_CARGO")

    resp = requests.post(f"{BASE_URL}/api/generate-token", json={"user_id": user_id, "cargo": cargo})
    assert resp.status_code == 200
    return resp.json()["token"]

def test_enviar_trafego(token):
    """
    Testa o endpoint de envio de tráfego para uma URL.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "service_id": 171,
        "url": "https://apretailer.com.br/click/67c140362bfa8136ea48f2f9/185510/349334/subaccount",
        "quantidade": 10
    }

    response = requests.post(f"{BASE_URL}/api/trafego/send", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "pedido_api" in data
    assert "preco_total" in data
    assert data["preco_total"] > 0
