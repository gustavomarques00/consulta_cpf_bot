from flask import request, jsonify
from functools import wraps
import jwt
import os

JWT_SECRET = os.getenv('JWT_SECRET', 'secretdoapp')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token ausente!'}), 401
        try:
            if token.startswith("Bearer "):
                token = token.split(" ")[1]
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            request.user_id = data['user_id']
            request.cargo = data.get('cargo', 'Usuario')  # Armazena cargo no request
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
