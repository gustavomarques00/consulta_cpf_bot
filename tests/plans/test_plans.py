import pytest
from services.token_service import TokenService
from services.plan_service import PlanService
from core.config import Config

# Configurações para o TokenService
JWT_SECRET = "defaultsecret"
JWT_ALGORITHM = "HS256"
token_service = TokenService(jwt_secret=JWT_SECRET, jwt_algorithm=JWT_ALGORITHM)
plan_service = PlanService()  # Exemplo de inicialização do serviço de planos

# ==== TESTES PÚBLICOS ====


def test_get_plans():
    """Testa se o serviço retorna uma lista de planos."""
    plans = plan_service.get_all_plans()
    assert isinstance(plans, list) and len(plans) > 0, "Nenhum plano retornado"


# ==== TESTES AUTENTICADOS ====


def test_get_user_plan():
    """
    Testa se o serviço retorna o plano do usuário autenticado.
    """
    user_id = 1  # ID do Chefe de Equipe
    user_plan = plan_service.get_user_plan(user_id)
    assert user_plan is not None, "Plano do usuário não encontrado"
    assert "id" in user_plan and "nome" in user_plan, "Dados do plano incompletos"
    assert user_plan["id"] == 1, "ID do plano incorreto"
    assert user_plan["nome"] == "Diário", "Nome do plano incorreto"


# ==== TESTES DE ERRO COM TOKEN ====


def test_protected_route_without_token():
    """Acesso sem token deve retornar erro."""
    with pytest.raises(ValueError, match="Token inválido!"):
        token_service.decode_token(None)


def test_protected_route_with_invalid_token():
    """Acesso com token inválido deve retornar erro."""
    invalid_token = "token_invalido"
    with pytest.raises(ValueError, match="Token inválido"):
        token_service.decode_token(invalid_token)


# ==== TESTES DE REFRESH TOKEN ====


def test_revoke_refresh_token():
    """Revoga um refresh_token gerado dinamicamente."""
    # Gera tokens
    tokens = token_service.generate_and_store_token(9, "ADM")
    refresh_token = tokens["refresh_token"]

    # Revoga o refresh_token
    token_service.revogar_refresh_token(refresh_token)

    # Verifica se o refresh_token foi revogado
    with pytest.raises(ValueError, match="Token inválido!"):
        token_service.decode_refresh_token(refresh_token)


def test_refresh_token_generates_new_access_token():
    """
    Testa se um refresh_token válido gera um novo access_token.
    """
    # Gera tokens iniciais
    tokens = token_service.generate_and_store_token(9, "ADM")
    refresh_token = tokens["refresh_token"]

    # Usa o refresh_token para gerar um novo access_token
    new_access_token = token_service.renovar_access_token(refresh_token)
    decoded_token = token_service.decode_token(new_access_token)

    # Verifica se o novo access_token é válido e contém os dados esperados
    assert (
        decoded_token["user_id"] == 9
    ), "Novo access_token não contém o user_id correto"
    assert (
        decoded_token["cargo"] == "ADM"
    ), "Novo access_token não contém o cargo correto"


# ==== TESTES DE REVOGAÇÃO ====


def test_revoke_token():
    """Revoga o próprio token."""
    # Gera tokens
    tokens = token_service.generate_and_store_token(9, "ADM")
    access_token = tokens["access_token"]

    # Revoga o token
    token_service.revogar_access_token(access_token)

    # Verifica se o token foi revogado
    with pytest.raises(ValueError, match="Token inválido!"):
        token_service.decode_token(access_token)


# ==== TESTE DE LISTAGEM DE REFRESH TOKENS ADMIN ====


def test_list_refresh_tokens_paginated():
    """Testa paginação e filtros da listagem de tokens."""
    # Gera tokens
    tokens = token_service.generate_and_store_token(9, "ADM")
    access_token = tokens["access_token"]

    # Listagem de tokens
    result = token_service.listar_refresh_tokens(
        page=1, limit=5, email_filter="adm", revogado_filter="false"
    )
    assert "data" in result, "Resposta não contém 'data'"
    assert isinstance(result["data"], list), "Dados retornados não são uma lista"
