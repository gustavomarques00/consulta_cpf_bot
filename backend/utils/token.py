import jwt
import os
import datetime
from core.db import get_db_connection

# Carrega variáveis de ambiente para segurança do JWT
JWT_SECRET = os.getenv("JWT_SECRET", "secretdoapp")  # A chave secreta do JWT
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")  # Algoritmo de criptografia do JWT

# Verificação da configuração do segredo e algoritmo (pode ser uma boa prática)
if not JWT_SECRET:
    raise ValueError("JWT_SECRET não está configurado!")
if not JWT_ALGORITHM:
    raise ValueError("JWT_ALGORITHM não está configurado!")


def generate_token(user_id, cargo):
    """
    Gera um token JWT de acesso (access_token) com 2 horas de validade.
    Inclui informações do usuário, como ID e cargo, no payload.
    """
    expiration_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        hours=2
    )

    payload = {
        "user_id": user_id,
        "cargo": cargo,
        "type": "access",  # Tipo de token, neste caso é um 'access' token
        "exp": expiration_date,  # Tempo de expiração
    }

    # Gera o token usando a chave secreta e o algoritmo configurado
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def generate_expired_token(user_id, cargo):
    """
    Gera um token JWT de acesso (access_token) que já está expirado.
    Inclui informações do usuário, como ID e cargo, no payload.
    """
    expired_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
        days=1
    )  # Definindo uma expiração no passado
    payload = {
        "user_id": user_id,
        "cargo": cargo,
        "type": "access",
        "exp": expired_date,
    }
    return jwt.encode(payload, "secretdoapp", algorithm="HS256")


def create_refresh_token(user_id):
    """
    Cria um token JWT de atualização (refresh_token) com validade de 7 dias.
    Contém apenas o ID do usuário.
    """
    expiration_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        days=7
    )

    payload = {
        "user_id": user_id,
        "type": "refresh",  # Tipo de token, neste caso é um 'refresh' token
        "exp": expiration_date,  # Tempo de expiração
    }

    # Gera o refresh token usando a chave secreta e o algoritmo configurado
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token):
    """
    Decodifica o token JWT e retorna os dados contidos nele.
    Retorna None em caso de erro, e imprime o erro para debug.
    """
    try:
        # Decodifica o token usando a chave secreta e o algoritmo configurado
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
    access_token = generate_token(user_id, cargo)  # Gera o access token
    refresh_token = create_refresh_token(user_id)  # Gera o refresh token
    return {"access_token": access_token, "refresh_token": refresh_token}


def generate_and_store_access_token(user_id, cargo):
    """
    Gera um access_token e o armazena no banco de dados.
    Retorna o access_token gerado.
    """
    access_token = generate_token(user_id, cargo)  # Gera o token
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tokens (usuario_id, plano_id, token, criado_em, expira_em) VALUES (%s, %s, %s, %s, %s)",
        (
            user_id,
            None,  # Não estamos utilizando plano_id aqui, mas pode ser adicionado
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
    """
    Revoga um token de acesso, adicionando-o à blacklist de tokens inválidos.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO token_blacklist (token, invalidado_em) VALUES (%s, %s)",
        (token, datetime.datetime.now(datetime.timezone.utc)),
    )

    conn.commit()
    cursor.close()
    conn.close()
