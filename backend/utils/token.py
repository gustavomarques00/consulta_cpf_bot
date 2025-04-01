from core.db import get_db_connection
import jwt
import os
import datetime

JWT_SECRET = os.getenv("JWT_SECRET", "secretdoapp")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def generate_token(user_id, cargo):
    """
    Gera um token JWT de acesso (access_token) com 15 minutos de validade.
    Inclui informações do usuário, como ID e cargo, no payload.
    """
    expiration_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        hours=2
    )
    payload = {
        "user_id": user_id,
        "cargo": cargo,
        "type": "access",
        "exp": expiration_date,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id):
    """
    Cria um token JWT de atualização (refresh_token) com validade de 7 dias.
    Contém apenas o ID do usuário.
    """
    expiration_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        days=7
    )
    payload = {"user_id": user_id, "type": "refresh", "exp": expiration_date}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token):
    """
    Decodifica o token JWT e retorna os dados contidos nele.
    Retorna None em caso de erro, e imprime o erro para debug.
    """
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        print("⚠️ Token expirado")
        return None
    except jwt.InvalidTokenError as e:
        print(f"⚠️ Token inválido: {e}")
        return None


def generate_tokens(user_id, cargo):
    """
    Gera um access_token e um refresh_token para o usuário.
    Útil em fluxos de login e renovação de sessão.
    """
    access_token = generate_token(user_id, cargo)
    refresh_token = create_refresh_token(user_id)
    return {"access_token": access_token, "refresh_token": refresh_token}


def generate_and_store_access_token(user_id, cargo):
    access_token = generate_token(user_id, cargo)  # Função que gera o token
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tokens (usuario_id, plano_id, token, criado_em, expira_em) VALUES (%s, %s, %s, %s, %s)",
        (
            user_id,
            None,
            access_token,
            datetime.datetime.now(datetime.timezone.utc),
            datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2),
        ),
    )
    conn.commit()
    cursor.close()
    conn.close()
    return access_token


def revoke_token(token):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO token_blacklist (token, invalidado_em) VALUES (%s, %s)",
        (token, datetime.datetime.now(datetime.timezone.utc)),
    )
    conn.commit()
    cursor.close()
    conn.close()
