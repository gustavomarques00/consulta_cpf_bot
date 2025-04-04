from core.db import get_db_connection
import pytest
import requests
import os
from tests.conftest import BASE_URL

def test_enviar_trafego(token):
    """
    Testa o endpoint de envio de tráfego para uma URL.
    """
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    payload = {
        "service_id": 171,
        "url": "https://apretailer.com.br/click/67c140362bfa8136ea48f2f9/185510/349334/subaccount",
        "quantidade": 100,
    }

    response = requests.post(
        f"{BASE_URL}/api/trafego/send", json=payload, headers=headers
    )

    assert response.status_code == 200
    data = response.json()

    assert "order_id" in data  # ✅ Corrigido
    assert isinstance(data["order_id"], int)
    assert data["message"].startswith("✅")

def test_enviar_trafego_com_id_usuario(token):
    """
    Testa o envio de tráfego via API e verifica se o ID do usuário foi registrado corretamente no banco.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Dados fixos
    service_id = 171
    test_url = "https://apretailer.com.br/click/67c140362bfa8136ea48f2f9/185510/349334/subaccount"
    
    # Alterando a quantidade para um valor maior
    quantidade = 100  # Aumentando para 100, que pode ser o mínimo permitido pela API

    # Envia pedido via /api/trafego/send
    payload = {
        "service_id": service_id,
        "url": test_url,
        "quantidade": quantidade,
    }

    # Realiza a requisição
    resp = requests.post(f"{BASE_URL}/api/trafego/send", json=payload, headers=headers)

    # Logando a resposta para diagnóstico
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
    assert result["user_id"] == int(os.getenv("TEST_USER_ID")), f"Esperado user_id {os.getenv('TEST_USER_ID')}, mas obteve {result['user_id']}"


