import requests
from unittest.mock import patch
from tests.conftest import BASE_URL


def test_access_admin_route_without_permissions(headers, base_url, invalid_token):
    """
    Testa o acesso à rota administrativa sem permissões adequadas.
    Verifica se a tentativa de acessar a rota '/api/admin/refresh-tokens' com um token inválido
    resulta em um erro 401 (Unauthorized) e se a mensagem de erro contém a palavra 'Token inválido'.
    """
    # Fazendo a requisição para a rota admin/refresh-tokens com um token inválido
    response = requests.get(
        f"{base_url}/api/admin/refresh-tokens",
        headers={
            "Authorization": f"Bearer {invalid_token}",
            **headers,
        },  # Passando o token inválido no header
    )

    # Verificando se o código de status é 401 (não autorizado)
    assert response.status_code == 401

    # Verificando se a mensagem de erro contém a palavra "Token inválido"
    assert "Token inválido" in response.json().get("error", "")
