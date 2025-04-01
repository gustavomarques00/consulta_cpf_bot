# backend/services/auth_service.py

import datetime
from backend.core.db import get_db_connection
from utils.token import generate_token


def generate_and_store_access_token(user_id, cargo):
    """
    Gera e armazena um access_token no banco de dados, vinculado ao usuário.
    """
    access_token = generate_token(user_id, cargo)
    expira_em = datetime.datetime.utcnow() + datetime.timedelta(hours=2)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO tokens (usuario_id, plano_id, token, criado_em, expira_em)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (user_id, None, access_token, datetime.datetime.utcnow(), expira_em),
        )
        conn.commit()
    except Exception as e:
        print(f"❌ Erro ao salvar token no banco: {e}")
    finally:
        cursor.close()
        conn.close()

    return access_token


def revoke_token(token):
    """
    Revoga um token JWT adicionando-o a uma blacklist.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO token_blacklist (token, invalidado_em)
            VALUES (%s, %s)
            """,
            (token, datetime.datetime.utcnow()),
        )
        conn.commit()
    except Exception as e:
        print(f"❌ Erro ao revogar token: {e}")
    finally:
        cursor.close()
        conn.close()
