import pytest
from backend.services.admin_service import AdminService

# Instância do AdminService
admin_service = AdminService()

# ========================
# TESTES DE ROTAS ADMIN
# ========================


def test_revoke_refresh_token():
    """
    🔐 Testa a revogação de um refresh_token usando o AdminService.
    """
    # Geração de tokens para o usuário ADM (ID 9)
    tokens = admin_service.gerar_token(user_id=9, cargo="ADM")
    refresh_token = tokens["refresh_token"]

    # Revogação do refresh_token
    admin_service.revogar_refresh_token(refresh_token)

    # Verifica se o refresh_token foi revogado
    with pytest.raises(ValueError, match="Token inválido ou já revogado!"):
        admin_service.revogar_refresh_token(refresh_token)


def test_list_refresh_tokens_paginated():
    """
    📄 Testa a listagem de refresh tokens com paginação e filtros.
    """
    # Geração de tokens para o usuário ADM (ID 9)
    admin_service.gerar_token(user_id=9, cargo="ADM")

    # Listar os tokens com paginação e filtros
    result = admin_service.listar_refresh_tokens(
        page=1, limit=5, email_filter="admin", revogado_filter="false"
    )

    # Verifica se os dados retornados estão corretos
    assert "data" in result, "❌ 'data' não encontrado na resposta"
    assert isinstance(result["data"], list), "❌ 'data' não é uma lista"

    # Verifica se os tokens retornados não estão revogados
    for token in result["data"]:
        assert not token["revogado"], f"❌ Token revogado encontrado: {token}"
