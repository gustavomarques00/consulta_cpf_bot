import logging
from flask import Blueprint, request, jsonify  # type: ignore
from middlewares.auth_middleware import token_required
from services.brsmm_service import BrsmmService
from flasgger.utils import swag_from  # type: ignore

# Configuração do Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

brsmm_bp = Blueprint("brsmm", __name__, url_prefix="/api/brsmm")
api = BrsmmService()


@brsmm_bp.route("/services", methods=["GET"])
@token_required
@swag_from(
    {
        "tags": ["BRSMM"],
        "summary": "Listar serviços da API BRSMM",
        "responses": {
            200: {
                "description": "Lista de serviços disponíveis",
                "examples": {
                    "application/json": [
                        {"service": 1, "name": "Followers", "rate": "0.90"}
                    ]
                },
            }
        },
    }
)
def listar_servicos():
    logger.info("Iniciando consulta para listar serviços BRSMM.")
    try:
        services = api.get_services()
        if "error" in services:
            logger.error(f"Erro ao buscar serviços: {services['error']}")
            return jsonify({"error": services["error"]}), 500
        logger.info(f"Serviços encontrados: {len(services)}")
        return jsonify(services), 200
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar serviços: {str(e)}")
        return jsonify({"error": f"Erro ao buscar serviços: {str(e)}"}), 500


@brsmm_bp.route("/order", methods=["POST"])
@token_required
@swag_from(
    {
        "tags": ["BRSMM"],
        "summary": "Criar novo pedido de tráfego",
        "parameters": [
            {
                "name": "body",
                "in": "body",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "link": {"type": "string"},
                        "service_id": {"type": "integer"},
                        "quantity": {"type": "integer"},
                        "price_per_unit": {"type": "number"},
                    },
                    "required": ["link", "service_id", "quantity", "price_per_unit"],
                },
            }
        ],
        "responses": {
            200: {"description": "Pedido criado"},
            400: {"description": "Erro de validação"},
        },
    }
)
def criar_pedido():
    data = request.get_json()
    required_fields = ["link", "service_id", "quantity", "price_per_unit"]
    logger.info(f"Iniciando criação de pedido com os dados: {data}")

    # Validação de campos obrigatórios
    for field in required_fields:
        if field not in data:
            logger.warning(f"Campo obrigatório ausente: {field}")
            return jsonify({"error": f"Campo obrigatório ausente: {field}"}), 400

    # Validação de quantidade
    if not (50 <= data["quantity"] <= 10000):
        logger.warning(
            f"Quantidade inválida: {data['quantity']}. Deveria estar entre 50 e 10000."
        )
        return jsonify({"error": "Quantidade deve estar entre 50 e 10000"}), 400

    try:
        # Criar pedido na API BRSMM
        response = api.add_order(
            link=data["link"],
            service_id=data["service_id"],
            quantity=data["quantity"],
        )

        if "error" in response:
            logger.error(f"Erro ao criar pedido na API: {response['error']}")
            return jsonify({"error": response["error"]}), 500

        # Registrar pedido no banco de dados
        preco_total = data["quantity"] * data["price_per_unit"]
        api.registrar_pedido_usuario(
            user_id=request.user_id,
            pedido_api=response,
            service_id=data["service_id"],
            url=data["link"],
            quantidade=data["quantity"],
            preco_unitario=data["price_per_unit"],
            preco_total=preco_total,
        )

        logger.info(f"Pedido criado com sucesso: {response}")
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Erro ao criar pedido: {str(e)}")
        return jsonify({"error": f"Erro ao criar pedido: {str(e)}"}), 500


@brsmm_bp.route("/status/<int:order_id>", methods=["GET"])
@token_required
@swag_from(
    {
        "tags": ["BRSMM"],
        "summary": "Ver status de um pedido",
        "parameters": [
            {"name": "order_id", "in": "path", "required": True, "type": "integer"}
        ],
        "responses": {
            200: {
                "description": "Status do pedido",
                "examples": {
                    "application/json": {"status": "In progress", "remains": "10"}
                },
            }
        },
    }
)
def consultar_status(order_id):
    logger.info(f"Iniciando consulta do status para o pedido {order_id}")
    try:
        response = api.get_order_status(order_id)
        if "error" in response:
            logger.error(f"Erro ao consultar status: {response['error']}")
            return jsonify({"error": response["error"]}), 500
        logger.info(f"Status do pedido {order_id}: {response}")
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Erro ao consultar status do pedido {order_id}: {str(e)}")
        return jsonify({"error": f"Erro ao consultar status: {str(e)}"}), 500


@brsmm_bp.route("/balance", methods=["GET"])
@token_required
@swag_from(
    {
        "tags": ["BRSMM"],
        "summary": "Consultar saldo BRSMM",
        "responses": {
            200: {
                "description": "Saldo da conta",
                "examples": {
                    "application/json": {"balance": "85.10", "currency": "USD"}
                },
            }
        },
    }
)
def consultar_saldo():
    logger.info("Iniciando consulta de saldo BRSMM.")
    try:
        balance = api.get_balance()
        if "error" in balance:
            logger.error(f"Erro ao consultar saldo: {balance['error']}")
            return jsonify({"error": balance["error"]}), 500
        logger.info(f"Saldo encontrado: {balance}")
        return jsonify(balance), 200
    except Exception as e:
        logger.error(f"Erro ao consultar saldo: {str(e)}")
        return jsonify({"error": f"Erro ao consultar saldo: {str(e)}"}), 500
