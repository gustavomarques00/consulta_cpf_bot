from flask import request, jsonify
from functools import wraps
import jwt
import os
from utils.db import get_db_connection

JWT_SECRET = os.getenv('JWT_SECRET')
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET não configurado! Defina a variável de ambiente.")
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token or not token.startswith("Bearer "):
            return jsonify({"error": "Token ausente ou inválido!"}), 401
        token = token.split(" ")[1]

        # Verifica se está na blacklist
        if is_token_blacklisted(token):
            return jsonify({"error": "Token revogado!"}), 401

        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            print("Token decodificado:", data)  
            request.user_id = data['user_id']
            request.cargo = data['cargo']
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido!"}), 401

        return f(*args, **kwargs)
    return decorated

def only_super_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        cargo = getattr(request, 'cargo', None)
        if not cargo:
            return jsonify({"error": "Cargo não definido no token!"}), 403
        if cargo != 'ADM':
            return jsonify({"error": "Acesso negado! Apenas Super Admins (ADM) podem acessar esta rota."}), 403
        return f(*args, **kwargs)
    return decorated

def is_token_blacklisted(token):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM refresh_tokens WHERE token = %s AND revogado = TRUE", (token,))
        return cursor.fetchone() is not None
    finally:
        conn.close()

