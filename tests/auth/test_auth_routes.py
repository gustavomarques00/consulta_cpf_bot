import pytest
from services.token_service import TokenService
from services.admin_service import AdminService
from core.config import Config

# Configurações para o TokenService
JWT_SECRET = "defaultsecret"
JWT_ALGORITHM = "HS256"
token_service = TokenService(jwt_secret=JWT_SECRET, jwt_algorithm=JWT_ALGORITHM)

# Configurações para o AdminService
admin_service = AdminService()

# ========================================
# TESTES DE GERAÇÃO, RENOVAÇÃO E REVOGAÇÃO
# ========================================


def test_generate_and_refresh_token():
    """
    🔄 Gera um refresh_token e o utiliza para obter novo access_token.

    Fluxo testado:
    - Gera tokens usando o TokenService
    - Usa o refresh_token para gerar um novo access_token
    """
    # Geração dos tokens para o usuário ADM (ID 9)
    tokens = token_service.generate_and_store_token(9, "ADM")
    assert (
        "access_token" in tokens and "refresh_token" in tokens
    ), "Tokens não retornados"

    # Renovação usando refresh_token
    refresh_token = tokens["refresh_token"]
    decoded_refresh_token = token_service.decode_refresh_token(refresh_token)
    assert decoded_refresh_token["user_id"] == 9, "Refresh token inválido"

    # Gera um novo access_token usando o refresh_token
    new_access_token = token_service.renovar_access_token(refresh_token)
    decoded_new_access_token = token_service.decode_token(new_access_token)
    assert decoded_new_access_token["user_id"] == 9, "Novo access_token inválido"
    assert (
        decoded_new_access_token["cargo"] == "ADM"
    ), "Novo access_token não contém o cargo correto"


def test_revoke_token():
    """
    ❌ Testa a revogação manual de um refresh_token usando o serviço AdminService.

    Verifica:
    - Se o token pode ser revogado com sucesso
    """
    # Geração de tokens para o usuário ADM (ID 9)
    tokens = token_service.generate_and_store_token(9, "ADM")
    refresh_token = tokens["refresh_token"]

    # Revogação do refresh_token usando o serviço
    admin_service.revogar_refresh_token(refresh_token)

    # Verifica se o refresh_token foi revogado
    with pytest.raises(ValueError, match="Token inválido!"):
        token_service.decode_refresh_token(refresh_token)


def test_revoke_refresh_token():
    """
    🔐 Revoga um refresh_token.

    Valida:
    - Geração de tokens válidos
    - Revogação do refresh_token
    """
    # Geração de tokens para o usuário ADM (ID 9)
    tokens = token_service.generate_and_store_token(9, "ADM")
    refresh_token = tokens["refresh_token"]

    # Revogação do refresh_token usando o TokenService
    token_service.revogar_refresh_token(refresh_token)

    # Verifica se o refresh_token foi revogado
    with pytest.raises(ValueError, match="Token inválido!"):
        token_service.decode_refresh_token(refresh_token)


def test_list_refresh_tokens_paginated():
    """
    📄 Lista todos os refresh tokens com paginação e filtros aplicados.

    Valida:
    - Geração de token de administrador
    - Listagem de tokens paginados
    """
    # Geração de token ADM (ID 9)
    tokens = token_service.generate_and_store_token(9, "ADM")

    # Listagem de tokens
    result = admin_service.listar_refresh_tokens(
        page=1, limit=5, email_filter="adm", revogado_filter="false"
    )
    assert "data" in result, "Resposta não contém 'data'"
    assert isinstance(result["data"], list), "Dados retornados não são uma lista"
    assert len(result["data"]) <= 5, "Mais de 5 tokens retornados"
