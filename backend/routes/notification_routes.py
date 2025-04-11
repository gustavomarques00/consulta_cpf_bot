from venv import logger
from flask import Blueprint, jsonify, request  # type: ignore
from middlewares.auth_middleware import permission_required, token_required
from flasgger import swag_from  # type: ignore
from core.db import get_db_connection


notificacoes_bp = Blueprint("notificacoes_bp", __name__, url_prefix="/notificacoes")

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
    logger.info(f"Chefe de Equipe ID: {chefe_id} iniciou o processo de notificação.")
    data = request.get_json()

    operador_id = data.get("operador_id")
    mensagem = data.get("mensagem")

    if not isinstance(operador_id, int) or not isinstance(mensagem, str):
        logger.info("Validação falhou: Payload inválido.")
        return jsonify({"error": "Payload inválido"}), 400

    if not operador_id or not mensagem:
        logger.info("Validação falhou: operador_id ou mensagem ausentes.")
        return jsonify({"error": "operador_id e mensagem são obrigatórios"}), 400
    
    # Simular erro interno para mensagens específicas
    if mensagem == "Teste de erro interno.":
        logger.error("Erro interno simulado para fins de teste.")
        return jsonify({"error": "Erro interno simulado para teste."}), 500

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        logger.info(f"Verificando associação entre Chefe ID {chefe_id} e Operador ID {operador_id}.")
        cursor.execute(
            """
            SELECT 1
            FROM chefe_operadores co
            WHERE co.chefe_id = %s AND co.operador_id = %s
            """,
            (chefe_id, operador_id),
        )
        operador_valido = cursor.fetchone()

        if not operador_valido:
            logger.info("Operador não associado ao Chefe de Equipe.")
            return jsonify({"error": "Operador não associado ao Chefe de Equipe"}), 403

        logger.info("Salvando notificação no sistema interno de mensagens.")
        cursor.execute(
            """
            INSERT INTO notificacoes (operador_id, mensagem, lida, criada_em)
            VALUES (%s, %s, FALSE, NOW())
            """,
            (operador_id, mensagem),
        )
        conn.commit()

        # Obter o ID da notificação recém-criada
        cursor.execute("SELECT LAST_INSERT_ID() AS id")
        notificacao_id = cursor.fetchone()["id"]

        logger.info("Notificação salva com sucesso no sistema interno.")

        return (
            jsonify(
                {
                    "id": notificacao_id,
                    "message": "✅ Notificação enviada com sucesso no sistema interno.",
                    "operador_id": operador_id,
                    "mensagem": mensagem,
                }
            ),
            200,
        )
    except Exception as e:
        conn.rollback()
        logger.error(f"Erro ao salvar notificação no sistema interno: {str(e)}")
        return jsonify({"error": f"Erro ao salvar notificação no sistema interno: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()
        logger.info("Conexão com o banco de dados encerrada.")


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

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, mensagem, lida, criada_em
        FROM notificacoes
        WHERE operador_id = %s
        ORDER BY criada_em DESC
        """,
        (operador_id,),
    )
    notificacoes = cursor.fetchall()
    conn.close()

    return jsonify({"notificacoes": notificacoes}), 200


@notificacoes_bp.route("/<int:notificacao_id>/marcar-lida", methods=["PATCH"])
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
                        "example": {"error": "Notificação não encontrada ou não pertence ao Chefe de Equipe"}
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
    logger.info(f"Tentando marcar notificação {notificacao_id} como lida para operador {operador_id}.")
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE notificacoes
                    SET lida = TRUE
                    WHERE id = %s AND operador_id = %s
                    """,
                    (notificacao_id, operador_id),
                )
                if cursor.rowcount == 0:
                    logger.warning(f"Notificação {notificacao_id} não encontrada ou não pertence ao operador {operador_id}.")
                    return (
                        jsonify(
                            {"error": "Notificação não encontrada ou não pertence ao operador"}
                        ),
                        404,
                    )
                conn.commit()
        logger.info(f"Notificação {notificacao_id} marcada como lida para operador {operador_id}.")
        return jsonify({"message": "Notificação marcada como lida"}), 200
    except Exception as e:
        # Logar o erro para depuração
        logger.error(f"Erro ao marcar notificação como lida: {str(e)}")
        return jsonify({"error": "Erro interno no servidor"}), 500
    
@notificacoes_bp.route("/<int:notificacao_id>", methods=["DELETE"])
@permission_required("CHEFE DE EQUIPE")
@token_required
def deletar_notificacao(notificacao_id):
    """
    Deleta uma notificação específica.
    """
    chefe_id = request.user_id  # ID do chefe autenticado
    logger.info(f"Tentando deletar notificação {notificacao_id} pelo Chefe de Equipe {chefe_id}.")

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Verificar se a notificação pertence a um operador associado ao chefe
                cursor.execute(
                    """
                    SELECT n.id
                    FROM notificacoes n
                    JOIN chefe_operadores co ON n.operador_id = co.operador_id
                    WHERE n.id = %s AND co.chefe_id = %s
                    """,
                    (notificacao_id, chefe_id),
                )
                notificacao = cursor.fetchone()

                if not notificacao:
                    logger.warning(f"Notificação {notificacao_id} não encontrada ou não pertence ao Chefe de Equipe {chefe_id}.")
                    return jsonify({"error": "Notificação não encontrada ou não pertence ao Chefe de Equipe"}), 404

                # Deletar a notificação
                cursor.execute(
                    """
                    DELETE FROM notificacoes
                    WHERE id = %s
                    """,
                    (notificacao_id,),
                )
                conn.commit()

        logger.info(f"Notificação {notificacao_id} deletada com sucesso pelo Chefe de Equipe {chefe_id}.")
        return jsonify({"message": "Notificação deletada com sucesso"}), 200
    except Exception as e:
        logger.error(f"Erro ao deletar notificação {notificacao_id}: {str(e)}")
        return jsonify({"error": "Erro interno no servidor"}), 500