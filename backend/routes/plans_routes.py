from requests import request
from middlewares.auth_middleware import token_required
from services.plan_service import PlanService
from flask import Blueprint, jsonify  # type: ignore
import logging
from flasgger import swag_from  # type: ignore

plans_bp = Blueprint("plans_bp", __name__, url_prefix="/servicos")
plan_service = PlanService()
logger = logging.getLogger(__name__)


@plans_bp.route("/plans", methods=["GET"])
@swag_from(
    {
        "tags": ["Planos"],
        "responses": {
            200: {"description": "Lista de planos com id, nome, preço e features"},
            404: {"description": "Nenhum plano encontrado"},
            500: {"description": "Erro ao consultar o banco"},
        },
    }
)
def get_plans():
    try:
        logger.info("Iniciando consulta de planos disponíveis.")
        plans = plan_service.get_all_plans()
        if not plans:
            logger.warning("Nenhum plano encontrado.")
            return jsonify({"error": "Nenhum plano encontrado!"}), 404

        logger.info("Consulta de planos concluída com sucesso.")
        return jsonify(plans), 200
    except Exception as err:
        logger.error(f"Erro ao consultar planos: {str(err)}")
        return jsonify({"error": str(err)}), 500


@plans_bp.route("/user-plans", methods=["GET"])
@token_required
@swag_from(
    {
        "tags": ["Planos"],
        "security": [{"Bearer": []}],
        "responses": {
            200: {"description": "Detalhes do plano do usuário"},
            401: {"description": "Token inválido ou ausente"},
            404: {"description": "Plano não encontrado para o usuário"},
        },
    }
)
def get_user_plan():
    user_id = request.user_id
    try:
        logger.info(f"Iniciando consulta do plano para o usuário {user_id}.")
        user_plan = plan_service.get_user_plan(user_id)

        if not user_plan:
            logger.warning(f"Plano não encontrado para o usuário {user_id}.")
            return jsonify({"error": "Plano não encontrado!"}), 404

        logger.info(
            f"Consulta do plano concluída com sucesso para o usuário {user_id}."
        )
        return jsonify(user_plan), 200
    except Exception as err:
        logger.error(f"Erro ao consultar plano do usuário {user_id}: {str(err)}")
        return jsonify({"error": str(err)}), 500
