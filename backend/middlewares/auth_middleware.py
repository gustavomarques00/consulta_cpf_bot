from venv import logger
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

        # Verifica se o cabeçalho Authorization está presente
        if not auth_header:
            return jsonify({"error": "Token não fornecido!"}), 401

        # Verifica se o cabeçalho começa com "Bearer "
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token inválido ou malformado!"}), 401

        # Extrai o token do cabeçalho
        token = auth_header.split("Bearer ")[-1].strip()

        # Verifica se o token está presente
        if not token:
            return jsonify({"error": "Token inválido ou ausente"}), 401

        # Verifica se o token está na lista de tokens revogados
        if is_token_blacklisted(token):
            return jsonify({"error": "Token revogado!"}), 401

        try:
            # Decodifica o token JWT
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            request.user_id = data.get("user_id")
            request.cargo = data.get("cargo")
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


def permission_required(required_role):
    """
    Verifica se o usuário autenticado tem a permissão necessária.
    :param required_role: O papel necessário para acessar a rota (ex: 'ADM', 'CHEFE DE EQUIPE', 'OPERADOR').
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return jsonify({"error": "Token não fornecido"}), 401

            if not auth_header.startswith("Bearer "):
                return jsonify({"error": "Token inválido ou malformado"}), 401

            token = auth_header.split("Bearer ")[-1].strip()
            if not token:
                return jsonify({"error": "Token não fornecido"}), 401

            user_data = decode_token(token)
            if not user_data:
                return jsonify({"error": "Token inválido"}), 401

            user_id = user_data.get("user_id")
            if not user_id:
                return jsonify({"error": "Token inválido: ID do usuário não encontrado"}), 401

            try:
                with get_db_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(
                            "SELECT cargo FROM usuarios WHERE id = %s", (user_id,)
                        )
                        user_role = cursor.fetchone()

                        if not user_role:
                            return jsonify({"error": "Usuário não encontrado"}), 404

                        # Log para depuração
                        logger.info(f"Cargo do usuário: {user_data.get('cargo')}, Cargo necessário: {required_role}")

                        # Verificar se o cargo do usuário corresponde ao necessário
                        if user_data.get("cargo") != required_role:
                            return jsonify({"error": "Acesso negado: Permissão insuficiente"}), 403

            except Exception as e:
                logger.error(f"Erro ao verificar permissão: {str(e)}")
                return jsonify({"error": "Erro interno no servidor"}), 500

            return f(*args, **kwargs)

        return decorated_function

    return decorator