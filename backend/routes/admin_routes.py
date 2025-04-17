import logging
from flask import Blueprint, jsonify, request  # type: ignore
from flasgger.utils import swag_from  # type: ignore
from middlewares.auth_middleware import token_required, only_super_admin
from services import token_service
from services.admin_service import AdminService

# Configuração do Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin")
admin_service = AdminService()


@admin_bp.route("/refresh-tokens", methods=["GET"])
@token_required
@only_super_admin
@swag_from(
    {
        "tags": ["Administração"],
        "summary": "Lista todos os refresh tokens com paginação e filtros opcionais.",
        "description": "Endpoint para listar refresh tokens com suporte a paginação e filtros opcionais, como email e status de revogação.",
        "parameters": [
            {
                "name": "page",
                "in": "query",
                "type": "integer",
                "default": 1,
                "required": False,
                "description": "Número da página",
            },
            {
                "name": "limit",
                "in": "query",
                "type": "integer",
                "default": 10,
                "required": False,
                "description": "Limite de itens por página",
            },
            {
                "name": "email",
                "in": "query",
                "type": "string",
                "required": False,
                "description": "Filtrar pelo email do usuário",
            },
            {
                "name": "revogado",
                "in": "query",
                "type": "boolean",
                "required": False,
                "description": "Filtrar por status de revogação (true ou false)",
            },
        ],
        "responses": {
            200: {"description": "Tokens paginados com total_pages"},
            500: {"description": "Erro ao listar refresh tokens"},
        },
    }
)
def listar_refresh_tokens():
    """
    Lista todos os refresh tokens com paginação e filtros opcionais.
    """
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        email_filter = request.args.get("email")
        revogado_filter = request.args.get("revogado")

        logger.info("Listando refresh tokens com paginação e filtros.")
        result = admin_service.listar_refresh_tokens(
            page, limit, email_filter, revogado_filter
        )
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Erro ao listar refresh tokens: {e}")
        return (
            jsonify({"error": "Erro ao listar refresh tokens.", "details": str(e)}),
            500,
        )


@admin_bp.route("/token-blacklist", methods=["GET"])
@token_required
@only_super_admin
@swag_from(
    {
        "tags": ["Administração"],
        "summary": "Lista tokens de access revogados (paginado).",
        "description": "Endpoint para listar tokens de access revogados com suporte a paginação.",
        "parameters": [
            {
                "name": "page",
                "in": "query",
                "type": "integer",
                "default": 1,
                "required": False,
                "description": "Número da página",
            },
            {
                "name": "limit",
                "in": "query",
                "type": "integer",
                "default": 10,
                "required": False,
                "description": "Limite de itens por página",
            },
        ],
        "responses": {
            200: {"description": "Lista paginada de tokens revogados"},
            500: {"description": "Erro ao listar tokens revogados"},
        },
    }
)
def listar_tokens_revogados():
    """
    Lista tokens de access revogados (paginado).
    """
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))

        logger.info("Listando tokens de access revogados com paginação.")
        tokens = admin_service.listar_tokens_revogados(page, limit)
        return jsonify(tokens), 200
    except Exception as e:
        logger.error(f"Erro ao listar tokens revogados: {e}")
        return (
            jsonify({"error": "Erro ao listar tokens revogados.", "details": str(e)}),
            500,
        )


@admin_bp.route("/revoke-refresh-token", methods=["POST"])
@token_required
@only_super_admin
@swag_from(
    {
        "tags": ["Administração"],
        "summary": "Revoga um refresh token específico.",
        "description": "Endpoint para revogar um refresh token específico.",
        "parameters": [
            {
                "name": "body",
                "in": "body",
                "required": True,
                "description": "Refresh token a ser revogado",
                "schema": {
                    "type": "object",
                    "properties": {"refresh_token": {"type": "string"}},
                },
            }
        ],
        "responses": {
            200: {"description": "Refresh token revogado com sucesso"},
            400: {"description": "Token ausente"},
            500: {"description": "Erro ao revogar refresh token"},
        },
    }
)
def revogar_refresh_token():
    """
    Revoga um refresh token específico.
    """
    try:
        data = request.get_json()
        refresh_token = data.get("refresh_token")

        if not refresh_token:
            logger.warning("Refresh token ausente na requisição.")
            return jsonify({"error": "Refresh token ausente!"}), 400

        logger.info(f"Revogando refresh token: {refresh_token}")
        admin_service.revogar_refresh_token(refresh_token)
        return jsonify({"message": "Refresh token revogado com sucesso!"}), 200
    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Erro ao revogar refresh token: {e}")
        return (
            jsonify({"error": "Erro ao revogar refresh token.", "details": str(e)}),
            500,
        )


@admin_bp.route("/generate-token", methods=["POST"])
@swag_from(
    {
        "tags": ["Autenticação"],
        "summary": "Gera e armazena um token JWT vinculado ao usuário e plano.",
        "description": "Endpoint para gerar e armazenar um token JWT vinculado ao usuário e plano.",
        "parameters": [
            {
                "name": "body",
                "in": "body",
                "required": True,
                "description": "Dados necessários para gerar o token",
                "schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "integer"},
                        "cargo": {"type": "string"},
                    },
                },
            }
        ],
        "responses": {
            200: {"description": "Token gerado e armazenado com sucesso"},
            400: {"description": "user_id ausente"},
            404: {"description": "Plano do usuário não encontrado"},
            500: {"description": "Erro no banco de dados"},
        },
    }
)
def generate_and_store_token():
    """
    Gera e armazena um token JWT vinculado ao usuário e plano.
    """
    try:
        data = request.get_json()
        if not data or "user_id" not in data:
            logger.warning("user_id ausente na requisição.")
            return jsonify({"error": "user_id é obrigatório!"}), 400

        user_id = data["user_id"]
        cargo = data["cargo"]

        logger.info(f"Gerando token para user_id: {user_id}, cargo: {cargo}")
        tokens = admin_service.gerar_token(user_id, cargo)
        return (
            jsonify(
                {
                    "message": "Token gerado com sucesso!",
                    "token": tokens["access_token"],
                    "refresh_token": tokens["refresh_token"],
                }
            ),
            200,
        )
    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Erro ao gerar token: {e}")
        return jsonify({"error": "Erro interno ao gerar token."}), 500


@admin_bp.route("/refresh-token", methods=["POST"])
@swag_from(
    {
        "tags": ["Autenticação"],
        "summary": "Gera um novo token de acesso com base no Refresh Token enviado via header.",
        "description": "Endpoint para gerar um novo token JWT com base em um Refresh Token válido enviado no cabeçalho.",
        "parameters": [
            {
                "name": "Refresh-Token",
                "in": "header",
                "required": True,
                "type": "string",
                "description": "Token de renovação (válido por 30 dias)",
            }
        ],
        "responses": {
            200: {
                "description": "Novo token JWT gerado com sucesso",
                "schema": {
                    "type": "object",
                    "properties": {
                        "token": {
                            "type": "string",
                            "example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        }
                    },
                },
            },
            401: {
                "description": "Refresh token ausente, expirado ou inválido",
                "schema": {
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "Refresh token ausente!",
                        }
                    },
                },
            },
            500: {
                "description": "Erro ao gerar novo token",
                "schema": {
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "Erro ao gerar novo token.",
                        },
                        "details": {
                            "type": "string",
                            "example": "Detalhes do erro.",
                        },
                    },
                },
            },
        },
    }
)
def refresh_token():
    """
    Gera um novo token de acesso com base no Refresh Token enviado via header.
    """
    refresh_token = request.headers.get("Refresh-Token")
    if not refresh_token:
        return jsonify({"error": "Refresh token ausente!"}), 401

    try:
        novo_token = token_service.decode_refresh_token(refresh_token)
        return jsonify({"token": novo_token}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": "Erro ao gerar novo token.", "details": str(e)}), 500


@admin_bp.route("/revoke-token", methods=["POST"])
@token_required
@only_super_admin
@swag_from(
    {
        "tags": ["Administração"],
        "summary": "Revoga um access_token manualmente (blacklist).",
        "description": "Endpoint para revogar manualmente um access_token, adicionando-o à blacklist.",
        "parameters": [
            {
                "name": "body",
                "in": "body",
                "required": True,
                "description": "Access token a ser revogado",
                "schema": {
                    "type": "object",
                    "properties": {
                        "token": {
                            "type": "string",
                            "example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        }
                    },
                },
            }
        ],
        "responses": {
            200: {
                "description": "Token revogado com sucesso",
                "schema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "example": "Access token revogado com sucesso!",
                        }
                    },
                },
            },
            400: {
                "description": "Token ausente",
                "schema": {
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "Access token ausente!",
                        }
                    },
                },
            },
            500: {
                "description": "Erro ao revogar access token",
                "schema": {
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "Erro ao revogar access token.",
                        },
                        "details": {
                            "type": "string",
                            "example": "Detalhes do erro.",
                        },
                    },
                },
            },
        },
    }
)
def revoke_token():
    """
    Revoga um access_token manualmente (blacklist).
    """
    try:
        data = request.get_json()
        access_token = data.get("token")

        if not access_token:
            return jsonify({"error": "Access token ausente!"}), 400

        # Chamar o serviço para revogar o access_token
        token_service.revogar_access_token_service(access_token)

        return jsonify({"message": "Access token revogado com sucesso!"}), 200
    except Exception as e:
        return (
            jsonify({"error": "Erro ao revogar access token.", "details": str(e)}),
            500,
        )
