import os
import pytest
import requests
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")


@pytest.fixture
def token():
    resp = requests.post(
        f"{BASE_URL}/api/generate-token", json={"user_id": 4, "cargo": "ADM"}
    )
    return resp.json().get("token")


def test_historico_completo(token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/api/trafego/historico", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), dict)


def test_historico_por_data(token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(
        f"{BASE_URL}/api/trafego/historico?data=2025-04-01", headers=headers
    )
    assert resp.status_code in [200, 404]


def test_exportar_csv(token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(
        f"{BASE_URL}/api/trafego/exportar?data=2025-04-01", headers=headers
    )
    assert resp.status_code in [200, 404]
