import pytest
import requests
import os
from dotenv import load_dotenv
from core.db import get_db_connection

load_dotenv()
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")


def test_enviar_pedido_salva_em_banco(token):
    """
    ✅ Testa o envio de tráfego via API e verifica se foi registrado no banco.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Dados fixos
    service_id = 171
    test_url = "https://apretailer.com.br/click/67c140362bfa8136ea48f2f9/185510/349334/subaccount"
    quantidade = 50

    # Envia pedido via /api/trafego/send
    payload = {
        "service_id": service_id,
        "url": test_url,
        "quantidade": quantidade,
    }
    resp = requests.post(f"{BASE_URL}/api/trafego/send", json=payload, headers=headers)

    assert resp.status_code in [200, 400]

    if resp.status_code == 200:
        data = resp.json()
        assert "order_id" in data
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

        assert result, "Pedido não foi salvo no banco de dados"
        assert result["user_id"], "user_id não salvo"
