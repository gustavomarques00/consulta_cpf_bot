import pytest
import requests


def test_access_admin_route_without_permissions(headers, base_url):
    """
    Testa o acesso à rota administrativa sem permissões adequadas.
    Verifica se a tentativa de acessar a rota '/api/admin/refresh-tokens' com um token inválido
    resulta em um erro 401 (Unauthorized) e se a mensagem de erro contém a palavra 'Token inválido'.
    """
    response = requests.get(
        f"{base_url}/api/admin/refresh-tokens",
        headers={"Authorization": "Bearer invalid_token", **headers},
    )

    # Verificando se o código de status é 401 (não autorizado)
    assert response.status_code == 401

    # Verificando se a mensagem de erro contém a palavra "Token inválido"
    assert "Token inválido" in response.json().get("error", "")
