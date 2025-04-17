import os
import csv
from venv import logger
from core.db import get_db_connection
from flask import Blueprint, jsonify, request, send_file  # type: ignore
from datetime import datetime
from io import StringIO
from urllib.parse import urlparse
import logging
from flasgger import swag_from  # type: ignore
from core.config import Config
from middlewares.auth_middleware import token_required, permission_required
from services.trafego_service import TrafegoService


trafego_bp = Blueprint("trafego", __name__, url_prefix="/trafego")
logger = logging.getLogger(__name__)

trafego_service = TrafegoService()


@trafego_bp.route("/historico", methods=["GET"])
@permission_required("CHEFE DE EQUIPE")
@token_required
@swag_from(
    {
        "tags": ["Tráfego"],
        "summary": "Consultar histórico de envios de tráfego",
        "parameters": [
            {
                "name": "data",
                "in": "query",
                "description": "Data no formato YYYY-MM-DD",
                "schema": {"type": "string"},
            },
            {
                "name": "status",
                "in": "query",
                "description": "Filtro por status: sucesso ou erro",
                "schema": {"type": "string"},
            },
        ],
        "responses": {
            200: {"description": "Histórico retornado com sucesso"},
            404: {"description": "Log não encontrado"},
        },
    }
)
def consultar_historico():
    """
    Consulta o histórico de envios de tráfego com base em filtros opcionais.
    """
    data_param = request.args.get("data")
    status_param = request.args.get("status")

    logger.info(
        f"Usuário {request.user_id} iniciou consulta de histórico com filtros: data={data_param}, status={status_param}"
    )

    try:
        # Chama o serviço para buscar o histórico
        response = trafego_service.consultar_historico(data_param, status_param)
        logger.info(
            f"Consulta de histórico concluída com sucesso para o usuário {request.user_id}"
        )
        return jsonify(response), 200
    except ValueError as e:
        logger.warning(
            f"Erro de validação na consulta de histórico: {str(e)} para o usuário {request.user_id}"
        )
        return jsonify({"error": str(e)}), 400
    except FileNotFoundError:
        logger.warning(
            f"Log não encontrado para a data {data_param} na consulta de histórico do usuário {request.user_id}"
        )
        return jsonify({"error": "Log não encontrado para a data informada"}), 404
    except Exception as e:
        logger.error(
            f"Erro ao consultar histórico para o usuário {request.user_id}: {str(e)}"
        )
        return jsonify({"error": f"Erro ao consultar histórico: {str(e)}"}), 500


@trafego_bp.route("/exportar", methods=["GET"])
@permission_required("CHEFE DE EQUIPE")
@token_required
@swag_from(
    {
        "tags": ["Tráfego"],
        "summary": "Exportar log diário para CSV",
        "parameters": [
            {
                "name": "data",
                "in": "query",
                "required": True,
                "description": "Data no formato YYYY-MM-DD",
            }
        ],
        "responses": {
            200: {"description": "Arquivo CSV gerado com sucesso"},
            404: {"description": "Log não encontrado"},
        },
    }
)
def exportar_csv():
    """
    Exporta o log diário para um arquivo CSV.
    """
    data_param = request.args.get("data")
    if not data_param:
        logger.warning("Parâmetro 'data' ausente na requisição.")
        return jsonify({"error": "Parâmetro 'data' é obrigatório (YYYY-MM-DD)"}), 400

    try:
        # Chama o serviço para exportar o log
        logger.info(
            f"Usuário {request.user_id} solicitou exportação de log para a data {data_param}."
        )
        csv_file = trafego_service.exportar_log_csv(data_param)
        logger.info(
            f"Exportação de log concluída com sucesso para a data {data_param}."
        )
        return send_file(
            csv_file,
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"trafego_{data_param}.csv",
        )
    except ValueError as e:
        logger.warning(f"Erro de validação na exportação de log: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except FileNotFoundError:
        logger.warning(f"Log não encontrado para a data {data_param}.")
        return jsonify({"error": "Log não encontrado para a data informada"}), 404
    except Exception as e:
        logger.error(f"Erro inesperado ao exportar log: {str(e)}")
        return jsonify({"error": f"Erro ao exportar log: {str(e)}"}), 500


@trafego_bp.route("/send", methods=["POST"])
@permission_required("CHEFE DE EQUIPE")
@token_required
@swag_from(
    {
        "tags": ["Tráfego"],
        "summary": "Enviar tráfego manualmente para uma URL",
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "service_id": {"type": "integer"},
                            "url": {"type": "string"},
                            "quantidade": {"type": "integer"},
                        },
                        "required": ["service_id", "url", "quantidade"],
                    }
                }
            },
        },
        "responses": {
            200: {"description": "Tráfego enviado com sucesso"},
            400: {"description": "Erro de validação ou requisição"},
        },
    }
)
def enviar_trafego_manual():
    """
    Envia tráfego manualmente para uma URL e registra o pedido no banco de dados.
    """
    data = request.get_json()
    service_id = data.get("service_id")
    url = data.get("url")
    quantidade = data.get("quantidade")
    user_id = request.user_id  # O ID do usuário autenticado

    # Validação de campos obrigatórios
    if not all([service_id, url, quantidade]):
        logger.warning(f"Usuário {user_id} enviou dados incompletos: {data}")
        return (
            jsonify({"error": "Campos obrigatórios: service_id, url, quantidade"}),
            400,
        )

    # Validação de quantidade
    if not (50 <= quantidade <= 10000):
        logger.warning(f"Usuário {user_id} enviou quantidade inválida: {quantidade}")
        return jsonify({"error": "Quantidade deve estar entre 50 e 10000"}), 400

    # Validação de URL
    parsed_url = urlparse(url)
    if not parsed_url.scheme in ["http", "https"]:
        logger.warning(f"Usuário {user_id} enviou URL inválida: {url}")
        return jsonify({"error": "URL inválida. Use http:// ou https://"}), 400

    try:
        # Chama o serviço para enviar o tráfego
        logger.info(f"Usuário {user_id} iniciou envio de tráfego para {url}.")
        response = trafego_service.enviar_pedido(user_id, service_id, url, quantidade)

        if "error" in response:
            logger.error(f"Erro ao enviar tráfego para {url}: {response['error']}")
            return jsonify(response), 400

        logger.info(f"Usuário {user_id} enviou tráfego com sucesso: {response}")
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Erro inesperado ao enviar tráfego: {str(e)}")
        return jsonify({"error": f"Erro ao enviar tráfego: {str(e)}"}), 500


@trafego_bp.route("/historico/meus-pedidos", methods=["GET"])
@permission_required("CHEFE DE EQUIPE")
@token_required
@swag_from(
    {
        "tags": ["Tráfego"],
        "summary": "Listar todos os pedidos realizados pelo usuário autenticado",
        "parameters": [
            {
                "name": "status",
                "in": "query",
                "description": "Filtro por status do pedido",
                "schema": {"type": "string"},
            },
            {
                "name": "service_id",
                "in": "query",
                "description": "Filtro por ID do serviço",
                "schema": {"type": "integer"},
            },
            {
                "name": "data_inicio",
                "in": "query",
                "description": "Data de início no formato YYYY-MM-DD",
                "schema": {"type": "string"},
            },
            {
                "name": "data_fim",
                "in": "query",
                "description": "Data de fim no formato YYYY-MM-DD",
                "schema": {"type": "string"},
            },
            {
                "name": "page",
                "in": "query",
                "description": "Número da página para paginação",
                "schema": {"type": "integer", "default": 1},
            },
            {
                "name": "limit",
                "in": "query",
                "description": "Quantidade de itens por página",
                "schema": {"type": "integer", "default": 10},
            },
        ],
        "responses": {
            200: {"description": "Pedidos retornados com sucesso"},
            400: {"description": "Erro de validação ou requisição"},
            500: {"description": "Erro interno do servidor"},
        },
    }
)
def meus_pedidos():
    """
    Listar todos os pedidos realizados pelo usuário autenticado.
    Suporta filtros por status, service_id, intervalo de datas e paginação.
    """
    user_id = request.user_id  # O ID do usuário autenticado
    status = request.args.get("status")
    service_id = request.args.get("service_id")
    data_inicio = request.args.get("data_inicio")
    data_fim = request.args.get("data_fim")
    page = int(request.args.get("page", 1))  # Padrão: 1
    limit = int(request.args.get("limit", 10))  # Padrão: 10

    logger.info(
        f"Usuário {user_id} iniciou consulta de pedidos com filtros: "
        f"status={status}, service_id={service_id}, data_inicio={data_inicio}, data_fim={data_fim}, page={page}, limit={limit}"
    )

    try:
        # Chama o serviço para buscar os pedidos
        response = trafego_service.consultar_meus_pedidos(
            user_id=user_id,
            status=status,
            service_id=service_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            page=page,
            limit=limit,
        )
        logger.info(
            f"Consulta de pedidos concluída com sucesso para o usuário {user_id}."
        )
        return jsonify(response), 200
    except ValueError as e:
        logger.warning(
            f"Erro de validação na consulta de pedidos para o usuário {user_id}: {str(e)}"
        )
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Erro ao consultar pedidos para o usuário {user_id}: {str(e)}")
        return jsonify({"error": f"Erro ao consultar pedidos: {str(e)}"}), 500


@trafego_bp.route("/pedidos/<int:order_id>/status", methods=["GET"])
@token_required
@permission_required("CHEFE DE EQUIPE")
@swag_from(
    {
        "tags": ["Tráfego"],
        "summary": "Consultar status de um pedido específico",
        "parameters": [
            {
                "name": "order_id",
                "in": "path",
                "required": True,
                "description": "ID do pedido a ser consultado",
                "schema": {"type": "integer"},
            }
        ],
        "responses": {
            200: {"description": "Status do pedido retornado com sucesso"},
            404: {"description": "Pedido não encontrado"},
            500: {"description": "Erro interno do servidor"},
        },
    }
)
def status_pedido(order_id):
    """
    Verifica o status de um pedido específico.
    """
    try:
        # Log de início da consulta
        logger.info(
            f"Iniciando consulta de status para pedido {order_id} do usuário {request.user_id}"
        )

        # Chama o serviço para buscar o status do pedido
        response = trafego_service.consultar_status_pedido(order_id, request.user_id)

        if "error" in response:
            logger.warning(
                f"Pedido não encontrado ou erro ao consultar: user_id={request.user_id}, order_id={order_id}"
            )
            return jsonify(response), 404

        # Log de sucesso
        logger.info(
            f"Pedido encontrado: user_id={request.user_id}, order_id={order_id}, status={response['status']}"
        )
        return jsonify(response), 200

    except Exception as e:
        logger.error(
            f"Erro ao consultar status do pedido: order_id={order_id}, error={str(e)}"
        )
        return jsonify({"error": f"Erro ao consultar status do pedido: {str(e)}"}), 500


@trafego_bp.route("/pedidos/status", methods=["GET"])
@token_required
@permission_required("CHEFE DE EQUIPE")
@swag_from(
    {
        "tags": ["Tráfego"],
        "summary": "Consultar status de múltiplos pedidos",
        "parameters": [
            {
                "name": "order_ids",
                "in": "query",
                "required": True,
                "description": "Lista de IDs de pedidos separados por vírgula",
                "schema": {"type": "array", "items": {"type": "integer"}},
            }
        ],
        "responses": {
            200: {"description": "Status dos pedidos retornado com sucesso"},
            400: {"description": "Erro de validação ou requisição"},
            404: {"description": "Pedidos não encontrados"},
            500: {"description": "Erro interno do servidor"},
        },
    }
)
def status_multiplos_pedidos():
    """
    Verifica o status de múltiplos pedidos.
    """
    order_ids = request.args.getlist("order_ids")

    if not order_ids:
        logger.warning(f"Usuário {request.user_id} não forneceu IDs de pedidos.")
        return jsonify({"error": "É necessário passar ao menos um ID de pedido"}), 400

    try:
        # Chama o serviço para buscar o status dos pedidos
        logger.info(
            f"Usuário {request.user_id} iniciou consulta de status para múltiplos pedidos."
        )
        response = trafego_service.consultar_status_multiplos_pedidos(
            order_ids, request.user_id
        )

        if "error" in response:
            logger.warning(
                f"Erro ao consultar status de múltiplos pedidos: {response['error']}"
            )
            return jsonify(response), 404

        logger.info(
            f"Consulta de status concluída com sucesso para o usuário {request.user_id}."
        )
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Erro ao consultar status de múltiplos pedidos: {str(e)}")
        return (
            jsonify(
                {"error": f"Erro ao consultar status de múltiplos pedidos: {str(e)}"}
            ),
            500,
        )
