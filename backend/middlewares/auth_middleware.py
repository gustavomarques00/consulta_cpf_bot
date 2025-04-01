from flask import request, jsonify
from functools import wraps
import jwt
from core.db import get_db_connection
from core.config import Config

JWT_SECRET = Config.JWT_SECRET
JWT_ALGORITHM = Config.JWT_ALGORITHM


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token ausente ou inválido!"}), 401

        token = auth_header.split(" ")[1]

        if is_token_blacklisted(token):
            return jsonify({"error": "Token revogado!"}), 401

        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            request.user_id = data["user_id"]
            request.cargo = data["cargo"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido!"}), 401

        return f(*args, **kwargs)

    return decorated


def only_super_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        cargo = getattr(request, "cargo", None)
        if cargo != "ADM":
            return (
                jsonify(
                    {
                        "error": "Acesso negado! Apenas Super Admins (ADM) podem acessar esta rota."
                    }
                ),
                403,
            )
        return f(*args, **kwargs)

    return decorated


def is_token_blacklisted(token):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM refresh_tokens WHERE token = %s AND revogado = TRUE",
            (token,),
        )
        return cursor.fetchone() is not None
    finally:
        conn.close()
