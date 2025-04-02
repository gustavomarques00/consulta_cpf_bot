from flask import Blueprint, request, jsonify  # type: ignore
from middlewares.auth_middleware import token_required
from services.brsmm_service import BrsmmService
from flasgger.utils import swag_from  # type: ignore

brsmm_bp = Blueprint("brsmm", __name__, url_prefix="/api/brsmm")
api = BrsmmService()


@brsmm_bp.route("/services", methods=["GET"])
@token_required
@swag_from({
    "tags": ["BRSMM"],
    "summary": "Listar serviços da API BRSMM",
    "responses": {
        200: {
            "description": "Lista de serviços disponíveis",
            "examples": {"application/json": [{"service": 1, "name": "Followers", "rate": "0.90"}]},
        }
    },
})
def listar_servicos():
    try:
        services = api.get_services()
        return jsonify(services), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao buscar serviços: {str(e)}"}), 500


@brsmm_bp.route("/order", methods=["POST"])
@token_required
@swag_from({
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
                },
                "required": ["link", "service_id", "quantity"],
            },
        }
    ],
    "responses": {
        200: {"description": "Pedido criado"},
        400: {"description": "Erro de validação"},
    },
})
def criar_pedido():
    data = request.get_json()
    required_fields = ["link", "service_id", "quantity"]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Campo obrigatório ausente: {field}"}), 400

    if not (50 <= data["quantity"] <= 10000):
        return jsonify({"error": "Quantidade deve estar entre 50 e 10000"}), 400

    response = api.add_order(
        link=data["link"], service_id=data["service_id"], quantity=data["quantity"]
    )
    return jsonify(response), 200 if "order" in response else 400


@brsmm_bp.route("/status/<int:order_id>", methods=["GET"])
@token_required
@swag_from({
    "tags": ["BRSMM"],
    "summary": "Ver status de um pedido",
    "parameters": [{"name": "order_id", "in": "path", "required": True, "type": "integer"}],
    "responses": {
        200: {
            "description": "Status do pedido",
            "examples": {"application/json": {"status": "In progress", "remains": "10"}},
        }
    },
})
def consultar_status(order_id):
    try:
        response = api.get_order_status(order_id)
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao consultar status: {str(e)}"}), 500


@brsmm_bp.route("/balance", methods=["GET"])
@token_required
@swag_from({
    "tags": ["BRSMM"],
    "summary": "Consultar saldo BRSMM",
    "responses": {
        200: {
            "description": "Saldo da conta",
            "examples": {"application/json": {"balance": "85.10", "currency": "USD"}},
        }
    },
})
def consultar_saldo():
    try:
        return jsonify(api.get_balance()), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao consultar saldo: {str(e)}"}), 500
