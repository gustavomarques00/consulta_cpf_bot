from flask import request, jsonify  # type: ignore
from functools import wraps
import jwt  # type: ignore
from core.db import get_db_connection
from core.config import Config
from utils.token import decode_token

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

def permission_required(role):
    """
    Verifica se o usuário autenticado tem a permissão necessária.
    :param role: O papel necessário para acessar a rota (ex: 'ADM', 'CHEFE DE EQUIPE', 'OPERADOR').
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization').split("Bearer ")[-1]
            if not token:
                return jsonify({"error": "Token não fornecido"}), 401

            user_data = decode_token(token)
            if not user_data:
                return jsonify({"error": "Token inválido"}), 401

            # Conectar ao banco de dados e buscar o cargo do usuário
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT cargo FROM usuarios WHERE id = %s", (user_data["user_id"],))
            user_role = cursor.fetchone()

            if user_role is None:
                return jsonify({"error": "Usuário não encontrado"}), 404

            cursor.close()
            conn.close()

            # Verificar se o cargo do usuário corresponde ao necessário
            if user_role[0] != role:
                return jsonify({"error": "Acesso negado"}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator
