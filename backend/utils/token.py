import jwt
import os
import datetime

JWT_SECRET = os.getenv('JWT_SECRET', 'secretdoapp')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')

def generate_token(user_id, cargo):
    """
    Gera um token JWT para o usuário.
    O token tem validade de 2 horas.
    """

    expiration_date = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    payload = {
        "user_id": user_id,
        "cargo": cargo,
        "exp": expiration_date
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id):
    """
    Cria um refresh token para o usuário.
    O refresh token tem validade de 7 dias.
    """
    expiration_date = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    payload = {
        "user_id": user_id,
        "exp": expiration_date
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token):
    """
    Decodifica o token JWT e retorna os dados contidos nele.
    Se o token for inválido ou expirado, retorna None.
    """
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def generate_tokens(user_id, cargo):
    """
    Gera um access_token e um refresh_token para o usuário.
    """
    access_token = generate_token(user_id, cargo)
    refresh_token = create_refresh_token(user_id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

