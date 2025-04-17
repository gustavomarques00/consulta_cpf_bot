from flask import Blueprint, jsonify, request  # type: ignore
from middlewares.auth_middleware import permission_required, token_required
from flasgger import swag_from  # type: ignore
from services.notification_service import NotificationService

# Inicialização do Blueprint e do serviço
notificacoes_bp = Blueprint("notificacoes_bp", __name__, url_prefix="/notificacoes")
notification_service = NotificationService()


@notificacoes_bp.route("/notificar-operador", methods=["POST"])
@permission_required("CHEFE DE EQUIPE")
@swag_from(
    {
        "tags": ["Chefe de Equipe"],
        "summary": "Notificar Operador",
        "description": "Permite ao Chefe de Equipe enviar notificações para um Operador sobre novas distribuições de dados.",
        "parameters": [
            {
                "name": "operador_id",
                "in": "query",
                "type": "integer",
                "required": True,
                "description": "ID do Operador que será notificado.",
            },
            {
                "name": "mensagem",
                "in": "query",
                "type": "string",
                "required": True,
                "description": "Mensagem a ser enviada ao Operador.",
            },
        ],
        "responses": {
            200: {
                "description": "Notificação enviada com sucesso.",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "✅ Notificação enviada com sucesso.",
                            "operador_id": 1,
                            "mensagem": "Você recebeu novos dados para processar.",
                        }
                    }
                },
            },
            400: {
                "description": "Erro de validação nos dados de entrada.",
            },
            403: {
                "description": "Acesso negado. O usuário não tem permissão para acessar esta rota.",
            },
        },
    }
)
@token_required
def notificar_operador():
    """
    Permite ao Chefe de Equipe enviar notificações para um Operador sobre novas distribuições de dados.
    """
    chefe_id = request.user_id
    data = request.get_json()

    operador_id = data.get("operador_id")
    mensagem = data.get("mensagem")

    if not operador_id or not mensagem:
        return jsonify({"error": "operador_id e mensagem são obrigatórios"}), 400

    try:
        response, status = notification_service.notificar_operador(
            chefe_id, operador_id, mensagem
        )
        return jsonify(response), status
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": f"Erro ao enviar notificação: {str(e)}"}), 500


@notificacoes_bp.route("/geral", methods=["GET"])
@token_required
@swag_from(
    {
        "tags": ["Chefe de Equipe"],
        "summary": "Listar Notificações",
        "description": "Lista as notificações do operador autenticado.",
        "responses": {
            200: {
                "description": "Lista de notificações do operador.",
                "content": {
                    "application/json": {
                        "example": {
                            "notificacoes": [
                                {
                                    "id": 1,
                                    "mensagem": "Você recebeu novos dados para processar.",
                                    "lida": False,
                                    "criada_em": "2023-04-07T12:00:00",
                                }
                            ]
                        }
                    }
                },
            },
            403: {
                "description": "Acesso negado. O usuário não tem permissão para acessar esta rota.",
            },
        },
    }
)
def listar_notificacoes():
    """
    Lista as notificações do operador autenticado.
    """
    operador_id = request.user_id  # ID do operador autenticado
    try:
        response, status = notification_service.listar_notificacoes(operador_id)
        return jsonify(response), status
    except Exception as e:
        return jsonify({"error": f"Erro ao listar notificações: {str(e)}"}), 500


@notificacoes_bp.route("/<int:notificacao_id>/marcar-lida", methods=["PATCH"])
@token_required
@swag_from(
    {
        "tags": ["Chefe de Equipe"],
        "summary": "Marcar Notificação como Lida",
        "description": "Permite ao operador marcar uma notificação como lida.",
        "parameters": [
            {
                "name": "notificacao_id",
                "in": "path",
                "type": "integer",
                "required": True,
                "description": "ID da notificação a ser marcada como lida.",
            }
        ],
        "responses": {
            200: {
                "description": "Notificação marcada como lida.",
                "content": {
                    "application/json": {
                        "example": {"message": "Notificação marcada como lida"}
                    }
                },
            },
            404: {
                "description": "Notificação não encontrada ou não pertence ao operador.",
                "content": {
                    "application/json": {
                        "example": {
                            "error": "Notificação não encontrada ou não pertence ao operador"
                        }
                    }
                },
            },
            500: {
                "description": "Erro interno no servidor.",
                "content": {
                    "application/json": {
                        "example": {"error": "Erro interno no servidor"}
                    }
                },
            },
        },
    }
)
def marcar_notificacao_como_lida(notificacao_id):
    """
    Marca uma notificação como lida.
    """
    operador_id = request.user_id  # ID do operador autenticado
    try:
        response, status = notification_service.marcar_notificacao_como_lida(
            operador_id, notificacao_id
        )
        return jsonify(response), status
    except Exception as e:
        return (
            jsonify({"error": f"Erro ao marcar notificação como lida: {str(e)}"}),
            500,
        )


@notificacoes_bp.route("/<int:notificacao_id>", methods=["DELETE"])
@permission_required("CHEFE DE EQUIPE")
@token_required
@swag_from(
    {
        "tags": ["Chefe de Equipe"],
        "summary": "Deletar Notificação",
        "description": "Permite ao Chefe de Equipe deletar uma notificação específica.",
        "parameters": [
            {
                "name": "notificacao_id",
                "in": "path",
                "type": "integer",
                "required": True,
                "description": "ID da notificação a ser deletada.",
            }
        ],
        "responses": {
            200: {
                "description": "Notificação deletada com sucesso.",
                "content": {
                    "application/json": {
                        "example": {"message": "Notificação deletada com sucesso"}
                    }
                },
            },
            404: {
                "description": "Notificação não encontrada ou não pertence ao Chefe de Equipe.",
                "content": {
                    "application/json": {
                        "example": {
                            "error": "Notificação não encontrada ou não pertence ao Chefe de Equipe"
                        }
                    }
                },
            },
            500: {
                "description": "Erro interno no servidor.",
                "content": {
                    "application/json": {
                        "example": {"error": "Erro interno no servidor"}
                    }
                },
            },
        },
    }
)
def deletar_notificacao(notificacao_id):
    """
    Deleta uma notificação específica.
    """
    chefe_id = request.user_id  # ID do chefe autenticado
    try:
        response, status = notification_service.deletar_notificacao(
            chefe_id, notificacao_id
        )
        return jsonify(response), status
    except Exception as e:
        return jsonify({"error": f"Erro ao deletar notificação: {str(e)}"}), 500
