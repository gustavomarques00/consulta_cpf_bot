from flask import Blueprint, jsonify, request
from utils.db import get_db_connection
from middlewares.auth import token_required, only_super_admin
import json
import datetime
from utils.token import generate_token

plans_bp = Blueprint('plans_bp', __name__)

@plans_bp.route('/api/plans', methods=['GET'])
def get_plans():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, preco, features FROM planos")
        plans = cursor.fetchall()
        for plan in plans:
            if isinstance(plan['features'], str):
                plan['features'] = json.loads(plan['features'])
            elif not isinstance(plan['features'], list):
                plan['features'] = []
        conn.close()

        if not plans:
            return jsonify({"error": "Nenhum plano encontrado!"}), 404

        return jsonify(plans), 200
    except Exception as err:
        return jsonify({"error": str(err)}), 500

@plans_bp.route('/api/user-plans', methods=['GET'])
@token_required
def get_user_plan():
    user_id = request.user_id
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id, p.nome, p.preco, p.features 
        FROM usuarios_planos up 
        JOIN planos p ON up.plano_id = p.id 
        WHERE up.usuario_id = %s
    """, (user_id,))
    user_plan = cursor.fetchone()
    conn.close()

    if not user_plan:
        return jsonify({"error": "Plano não encontrado!"}), 404

    return jsonify(user_plan), 200

@plans_bp.route('/api/generate-token', methods=['POST'])
def generate_and_store_token():
    data = request.get_json()
    user_id = data.get('user_id')
    cargo = data.get('cargo', 'Independente')

    if not user_id:
        return jsonify({"error": "user_id é obrigatório!"}), 400

    token = generate_token(user_id, cargo)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT plano_id FROM usuarios_planos WHERE usuario_id = %s", (user_id,))
    user_plan = cursor.fetchone()

    if not user_plan:
        return jsonify({"error": "Plano não encontrado!"}), 404

    plano_id = user_plan['plano_id']
    expira_em = datetime.datetime.utcnow() + datetime.timedelta(days=365 * 5)

    try:
        cursor.execute(
            "INSERT INTO tokens (usuario_id, plano_id, token, expira_em) VALUES (%s, %s, %s, %s)",
            (user_id, plano_id, token, expira_em)
        )
        conn.commit()
        conn.close()
        return jsonify({
            "message": "Token gerado com sucesso!",
            "token": token
        }), 200
    except Exception as err:
        conn.rollback()
        conn.close()
        return jsonify({"error": str(err)}), 500

@plans_bp.route('/api/superadmin/test', methods=['GET'])
@token_required
@only_super_admin
def test_superadmin():
    return jsonify({"message": f"Acesso liberado, Super Admin {request.user_id}!"})

