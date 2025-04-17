import pytest
from services.admin_service import AdminService


def test_access_admin_route_with_adm_token(chefe_token):
    """
    Testa o acesso à rota administrativa com um token válido de ADM.
    """
    # Instância do serviço AdminService
    admin_service = AdminService()

    # Configurando os parâmetros para listar os refresh tokens
    page = 1
    limit = 10

    # Chamando o método real do serviço
    response = admin_service.listar_refresh_tokens(page, limit)

    # Verificando se o retorno contém os dados esperados
    assert "page" in response, "❌ O retorno não contém o campo 'page'."
    assert "limit" in response, "❌ O retorno não contém o campo 'limit'."
    assert "total_pages" in response, "❌ O retorno não contém o campo 'total_pages'."
    assert (
        "total_results" in response
    ), "❌ O retorno não contém o campo 'total_results'."
    assert "data" in response, "❌ O retorno não contém o campo 'data'."
    assert isinstance(response["data"], list), "❌ O campo 'data' deve ser uma lista."

    # Verificando se os dados retornados estão no formato esperado
    if response["data"]:
        token = response["data"][0]
        assert (
            "id" in token
        ), "❌ O token retornado não contém o campo obrigatório 'id'."
        assert (
            "token" in token
        ), "❌ O token retornado não contém o campo obrigatório 'token'."
        assert (
            "revogado" in token
        ), "❌ O token retornado não contém o campo obrigatório 'revogado'."
        assert (
            "criado_em" in token
        ), "❌ O token retornado não contém o campo obrigatório 'criado_em'."
        assert (
            "expira_em" in token
        ), "❌ O token retornado não contém o campo obrigatório 'expira_em'."
        assert (
            "usuario_email" in token
        ), "❌ O token retornado não contém o campo obrigatório 'usuario_email'."
