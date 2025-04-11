import os
import pytest
import requests

from tests.conftest import BASE_URL

# Teste para verificar o histórico completo de tráfego.
def test_historico_completo(token, headers):
    """
    Testa o endpoint de histórico completo de tráfego.
    """
    auth_headers = {**headers, "Authorization": f"Bearer {token['token']}"}
    resp = requests.get(f"{BASE_URL}/trafego/historico", headers=auth_headers)
    assert resp.status_code == 200, f"Erro ao obter histórico completo: {resp.text}"
    assert isinstance(resp.json(), dict), "Resposta não é um JSON válido"

# Teste para verificar o histórico de tráfego filtrado por data.
def test_historico_por_data(token, headers):
    """
    Testa o endpoint de histórico de tráfego filtrado por data.
    """
    auth_headers = {**headers, "Authorization": f"Bearer {token['token']}"}
    resp = requests.get(
        f"{BASE_URL}/trafego/historico?data=2025-04-01", headers=auth_headers
    )
    assert resp.status_code in [200, 404], f"Erro ao filtrar histórico: {resp.text}"

# Teste para verificar a exportação de dados em formato CSV.
def test_exportar_csv(token, headers):
    """
    Testa o endpoint de exportação de tráfego em formato CSV.
    """
    auth_headers = {**headers, "Authorization": f"Bearer {token['token']}"}
    resp = requests.get(
        f"{BASE_URL}/trafego/exportar?data=2025-04-01", headers=auth_headers
    )
    assert resp.status_code in [200, 404], f"Erro ao exportar CSV: {resp.text}"