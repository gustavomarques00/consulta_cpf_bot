from flask import request, jsonify
from functools import wraps
import jwt
import os
from utils.db import get_db_connection

JWT_SECRET = os.getenv('JWT_SECRET', 'secretdoapp')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token ausente!'}), 401

        # Extrair token sem o prefixo "Bearer"
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
        else:
            return jsonify({"error": "Formato do token inválido!"}), 400

        # Verifica se está na blacklist
        if is_token_blacklisted(token):
            return jsonify({"error": "Token revogado!"}), 401

        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            request.user_id = data['user_id']
            request.cargo = data.get('cargo', 'Usuario')
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido!"}), 401

        return f(*args, **kwargs)
    return decorated

def only_super_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if getattr(request, 'cargo', None) != 'ADM':
            return jsonify({"error": "Acesso negado! Apenas Super Admins (ADM) podem acessar esta rota."}), 403
        return f(*args, **kwargs)
    return decorated

from utils.db import get_db_connection

def is_token_blacklisted(token):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM token_blacklist WHERE token = %s", (token,))
    return cursor.fetchone() is not None

