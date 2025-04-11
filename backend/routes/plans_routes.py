

from core.db import get_db_connection
from flask import Blueprint, jsonify, request
import os
import json
from middlewares.auth_middleware import token_required
from utils.parse_date import parse_date


plans_bp = Blueprint("plans_bp", __name__,url_prefix="/servicos")

JWT_SECRET = os.getenv("JWT_SECRET", "secretdoapp")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


@plans_bp.route("/plans", methods=["GET"])
def get_plans():
    """
    Retorna a lista de todos os planos disponíveis.
    ---
    tags:
      - Planos
    responses:
      200:
        description: Lista de planos com id, nome, preço e features
      404:
        description: Nenhum plano encontrado
      500:
        description: Erro ao consultar o banco
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, preco, features FROM planos")
        plans = cursor.fetchall()
        for plan in plans:
            if isinstance(plan["features"], str):
                plan["features"] = json.loads(plan["features"])
            elif not isinstance(plan["features"], list):
                plan["features"] = []
        conn.close()

        if not plans:
            return jsonify({"error": "Nenhum plano encontrado!"}), 404

        return jsonify(plans), 200
    except Exception as err:
        return jsonify({"error": str(err)}), 500


@plans_bp.route("/user-plans", methods=["GET"])
@token_required
def get_user_plan():
    """
    Retorna o plano associado ao usuário autenticado via token.
    ---
    tags:
      - Planos
    security:
      - Bearer: []
    responses:
      200:
        description: Detalhes do plano do usuário
      401:
        description: Token inválido ou ausente
      404:
        description: Plano não encontrado para o usuário
    """
    user_id = request.user_id
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT p.id, p.nome, p.preco, p.features, up.data_inicio, up.data_fim
        FROM usuarios_planos up 
        JOIN planos p ON up.plano_id = p.id 
        WHERE up.usuario_id = %s
        """,
        (user_id,),
    )
    user_plan = cursor.fetchone()
    conn.close()

    if not user_plan:
        return jsonify({"error": "Plano não encontrado!"}), 404

    # Formatar as datas no padrão brasileiro usando parse_date
    if user_plan["data_inicio"]:
        user_plan["data_inicio"] = parse_date(str(user_plan["data_inicio"]))
    if user_plan["data_fim"]:
        user_plan["data_fim"] = parse_date(str(user_plan["data_fim"]))

    return jsonify(user_plan), 200


