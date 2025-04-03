import os
import csv
from venv import logger
from core.db import get_db_connection
from flask import Blueprint, jsonify, request, send_file
from datetime import datetime
from io import StringIO
from urllib.parse import urlparse
from flasgger import swag_from
from backend.core.config import Config
from middlewares.auth_middleware import token_required

trafego_bp = Blueprint("trafego", __name__, url_prefix="/api/trafego")


@trafego_bp.route("/historico", methods=["GET"])
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
    data_param = request.args.get("data")
    status_param = request.args.get("status")
    log_dir = os.path.join(Config.BASE_DIR, "logs", "brsmm")

    if not os.path.exists(log_dir):
        return jsonify({"message": "Nenhum log disponível ainda."}), 200

    if data_param:
        try:
            datetime.strptime(data_param, "%Y-%m-%d")
        except ValueError:
            return (
                jsonify({"error": "Data inválida. Formato esperado: YYYY-MM-DD"}),
                400,
            )

        log_path = os.path.join(log_dir, f"brsmm_{data_param}.log")
        if not os.path.exists(log_path):
            return jsonify({"error": "Log não encontrado para a data informada"}), 404

        with open(log_path, "r", encoding="utf-8") as f:
            linhas = [l.strip() for l in f.readlines()]

        if status_param:
            status_param = status_param.lower()
            if status_param == "sucesso":
                linhas = [l for l in linhas if "✅" in l]
            elif status_param == "erro":
                linhas = [l for l in linhas if "❌" in l or "💥" in l]

        return jsonify({"data": linhas})

    historico = {}
    for nome in sorted(os.listdir(log_dir), reverse=True):
        if nome.startswith("brsmm_") and nome.endswith(".log"):
            data_log = nome.replace("brsmm_", "").replace(".log", "")
            with open(os.path.join(log_dir, nome), "r", encoding="utf-8") as f:
                linhas = [l.strip() for l in f.readlines()]
                if status_param:
                    if status_param == "sucesso":
                        linhas = [l for l in linhas if "✅" in l]
                    elif status_param == "erro":
                        linhas = [l for l in linhas if "❌" in l or "💥" in l]
                historico[data_log] = linhas

    return jsonify(historico)


@trafego_bp.route("/exportar", methods=["GET"])
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
    data_param = request.args.get("data")
    if not data_param:
        return jsonify({"error": "Parâmetro 'data' é obrigatório (YYYY-MM-DD)"}), 400

    try:
        datetime.strptime(data_param, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Data inválida. Formato esperado: YYYY-MM-DD"}), 400

    log_path = os.path.join(Config.BASE_DIR, "logs", "brsmm", f"brsmm_{data_param}.log")
    if not os.path.exists(log_path):
        return jsonify({"error": "Log não encontrado"}), 404

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Linha"])  # Pode-se refinar para colunas reais depois

    with open(log_path, "r", encoding="utf-8") as file:
        for linha in file:
            writer.writerow([linha.strip()])

    output.seek(0)
    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"trafego_{data_param}.csv",
    )


@trafego_bp.route("/send", methods=["POST"])
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
    from services.brsmm_service import BrsmmService

    data = request.get_json()
    service_id = data.get("service_id")
    url = data.get("url")
    quantidade = data.get("quantidade")

    if not all([service_id, url, quantidade]):
        return (
            jsonify({"error": "Campos obrigatórios: service_id, url, quantidade"}),
            400,
        )

    if not (50 <= quantidade <= 10000):
        return jsonify({"error": "Quantidade deve estar entre 50 e 10000"}), 400

    parsed_url = urlparse(url)
    if not parsed_url.scheme in ["http", "https"]:
        return jsonify({"error": "URL inválida. Use http:// ou https://"}), 400

    api = BrsmmService()
    response = api.add_order(link=url, service_id=service_id, quantity=quantidade)

    if "order" in response:
        return (
            jsonify(
                {
                    "message": "✅ Pedido enviado com sucesso",
                    "order_id": response["order"],
                }
            ),
            200,
        )
    else:
        return jsonify({"error": response}), 400


@trafego_bp.route("/historico/meus-pedidos", methods=["GET"])
@token_required
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
    offset = (page - 1) * limit  # Cálculo de offset para paginação

    filtros = ["user_id = %s"]  # Filtro inicial obrigatório
    params = [user_id]  # Parâmetros da query

    # Adicionar filtros dinâmicos
    if status:
        filtros.append("status = %s")
        params.append(status)

    if service_id:
        filtros.append("service_id = %s")
        params.append(service_id)

    if data_inicio:
        filtros.append("DATE(criado_em) >= %s")
        params.append(data_inicio)

    if data_fim:
        filtros.append("DATE(criado_em) <= %s")
        params.append(data_fim)

    # Construção da cláusula WHERE
    where_clause = " AND ".join(filtros)

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Contar o total de registros que atendem aos filtros (para calcular a paginação)
        cursor.execute(
            f"SELECT COUNT(*) as total FROM trafego_pedidos WHERE {where_clause}",
            params,
        )
        total = cursor.fetchone()["total"]
        total_pages = (total + limit - 1) // limit  # Cálculo do total de páginas

        # Buscar os registros paginados
        cursor.execute(
            f"""
            SELECT id, brsmm_order_id, service_id, url, quantidade, preco_total, status, criado_em
            FROM trafego_pedidos
            WHERE {where_clause}
            ORDER BY criado_em DESC
            LIMIT %s OFFSET %s
            """,
            params + [limit, offset],
        )
        pedidos = cursor.fetchall()
        cursor.close()
        conn.close()

        return (
            jsonify(
                {
                    "page": page,
                    "limit": limit,
                    "total_pages": total_pages,
                    "total_results": total,
                    "data": pedidos,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": f"Erro ao consultar pedidos: {str(e)}"}), 500

@trafego_bp.route("/pedidos/<int:order_id>/status", methods=["GET"])
@token_required
def status_pedido(order_id):
    """
    Verifica o status de um pedido específico.
    """
    try:
        # Log de início da consulta
        logger.info(f"Iniciando consulta de status para pedido {order_id} do usuário {request.user_id}")
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Verificar se o pedido existe
        cursor.execute(
            "SELECT * FROM trafego_pedidos WHERE brsmm_order_id = %s AND user_id = %s",
            (order_id, request.user_id),
        )
        pedido = cursor.fetchone()

        if not pedido:
            logger.warning(f"Pedido não encontrado: user_id={request.user_id}, order_id={order_id}")
            return jsonify({"error": "Pedido não encontrado para o usuário autenticado"}), 404

        cursor.close()
        conn.close()

        # Log de sucesso
        logger.info(f"Pedido encontrado: user_id={request.user_id}, order_id={order_id}, status={pedido['status']}")
        return jsonify({"status": pedido["status"], "data_criado_em": pedido["criado_em"]}), 200

    except Exception as e:
        logger.error(f"Erro ao consultar status do pedido: order_id={order_id}, error={str(e)}")
        return jsonify({"error": f"Erro ao consultar status do pedido: {str(e)}"}), 500




@trafego_bp.route("/pedidos/status", methods=["GET"])
@token_required
def status_multiplos_pedidos():
    """
    Verifica o status de múltiplos pedidos.
    """
    order_ids = request.args.getlist("order_ids")

    if not order_ids:
        return jsonify({"error": "É necessário passar ao menos um ID de pedido"}), 400

    order_ids_tuple = tuple(order_ids)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            f"SELECT * FROM trafego_pedidos WHERE brsmm_order_id IN ({','.join(['%s'] * len(order_ids))}) AND user_id = %s",
            tuple(order_ids) + (request.user_id,),
        )
        pedidos = cursor.fetchall()

        # Verifica se todos os pedidos foram encontrados, caso contrário retorna 404
        if len(pedidos) != len(order_ids):
            return jsonify({"error": "Nenhum pedido encontrado para os IDs fornecidos"}), 404
        
        cursor.close()
        conn.close()

        # Se encontrar, retorna a lista de pedidos com seus status
        return jsonify(
            [
                {"order_id": pedido["brsmm_order_id"], "status": pedido["status"]}
                for pedido in pedidos
            ]
        ), 200

    except Exception as e:
        # Caso ocorra algum erro no banco de dados ou outro erro interno
        return jsonify({"error": f"Erro ao consultar status de múltiplos pedidos: {str(e)}"}), 500

