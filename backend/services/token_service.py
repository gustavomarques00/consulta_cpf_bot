import jwt  # type: ignore
import datetime
from core.db import get_db_connection
import logging


class TokenService:
    def __init__(self, jwt_secret, jwt_algorithm):
        self.jwt_secret = jwt_secret
        self.jwt_algorithm = jwt_algorithm
        self.logger = logging.getLogger(__name__)

    def generate_access_token(self, user_id, cargo):
        """
        Gera um token JWT de acesso (access_token) com 2 horas de validade.
        """
        expiration_date = datetime.datetime.now(
            datetime.timezone.utc
        ) + datetime.timedelta(hours=2)
        payload = {
            "user_id": user_id,
            "cargo": cargo,
            "type": "access",
            "exp": expiration_date,
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def generate_refresh_token(self, user_id):
        """
        Cria um token JWT de atualização (refresh_token) com validade de 7 dias.
        """
        expiration_date = datetime.datetime.now(
            datetime.timezone.utc
        ) + datetime.timedelta(days=7)
        payload = {
            "user_id": user_id,
            "type": "refresh",
            "exp": expiration_date,
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def decode_token(self, token):
        """
        Decodifica um token JWT e verifica se ele foi revogado.
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Verifica se o token está na blacklist
            self.logger.info("Verificando se o token foi revogado.")
            cursor.execute("SELECT 1 FROM token_blacklist WHERE token = %s", (token,))
            if cursor.fetchone():
                raise ValueError("Token inválido!")

            # Decodifica o token
            return jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expirado!")
        except jwt.InvalidTokenError:
            raise ValueError("Token inválido!")
        finally:
            cursor.close()
            conn.close()

    def generate_and_store_token(self, user_id, cargo):
        """
        Gera e armazena tokens JWT (access_token e refresh_token) para um usuário.
        """
        self.logger.info(
            "Iniciando geração e armazenamento de tokens para o usuário %s", user_id
        )

        access_token = self.generate_access_token(user_id, cargo)
        refresh_token = self.generate_refresh_token(user_id)

        self.logger.debug(
            "Tokens gerados: access_token=%s, refresh_token=%s",
            access_token,
            refresh_token,
        )

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Verificar plano do usuário
            self.logger.info("Verificando plano do usuário %s", user_id)
            cursor.execute(
                "SELECT plano_id FROM usuarios_planos WHERE usuario_id = %s", (user_id,)
            )
            user_plan = cursor.fetchone()

            if not user_plan:
                self.logger.error("Plano não encontrado para o usuário %s", user_id)
                raise ValueError("Plano não encontrado!")

            # Definir expiração do refresh token (7 dias)
            expira_em = datetime.datetime.now() + datetime.timedelta(days=7)
            self.logger.debug("Expiração do refresh token definida para %s", expira_em)

            # Salvar refresh token no banco
            self.logger.info(
                "Salvando refresh token no banco para o usuário %s", user_id
            )
            cursor.execute(
                "DELETE FROM refresh_tokens WHERE usuario_id = %s", (user_id,)
            )
            cursor.execute(
                """
                INSERT INTO refresh_tokens (usuario_id, token, expira_em)
                VALUES (%s, %s, %s)
                """,
                (user_id, refresh_token, expira_em),
            )
            conn.commit()

            self.logger.info(
                "Tokens armazenados com sucesso para o usuário %s", user_id
            )
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        except Exception as e:
            conn.rollback()
            self.logger.error(
                "Erro ao salvar tokens no banco para o usuário %s: %s", user_id, e
            )
            raise ValueError(f"Erro ao salvar tokens no banco: {e}")
        finally:
            cursor.close()
            conn.close()
            self.logger.info("Conexão com o banco fechada")

    def listar_refresh_tokens(
        self, page, limit, email_filter=None, revogado_filter=None
    ):
        """
        Lista todos os refresh tokens com paginação e filtros opcionais.
        """
        offset = (page - 1) * limit

        base_query = """
            FROM refresh_tokens rt
            JOIN usuarios u ON rt.usuario_id = u.id
            WHERE 1=1
        """
        params = []

        if email_filter:
            base_query += " AND u.email LIKE %s"
            params.append(f"%{email_filter}%")

        if revogado_filter in ["true", "false"]:
            base_query += " AND rt.revogado = %s"
            params.append(revogado_filter.lower() == "true")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Total de resultados
            cursor.execute(f"SELECT COUNT(*) AS total {base_query}", params)
            total = cursor.fetchone()["total"]
            total_pages = (total + limit - 1) // limit

            # Resultados paginados
            cursor.execute(
                f"""
                SELECT rt.id, rt.token, rt.criado_em, rt.expira_em, rt.revogado,
                       u.id as usuario_id, u.email
                {base_query}
                ORDER BY rt.criado_em DESC
                LIMIT %s OFFSET %s
                """,
                (*params, limit, offset),
            )
            tokens = cursor.fetchall()

            return {
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "total_results": total,
                "data": tokens,
            }
        finally:
            cursor.close()
            conn.close()

    def listar_tokens_revogados(self, page, limit):
        """
        Lista tokens de access revogados com paginação.
        """
        offset = (page - 1) * limit

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Consulta os tokens revogados com paginação
            cursor.execute(
                """
                SELECT id, token, invalidado_em
                FROM token_blacklist
                ORDER BY invalidado_em DESC
                LIMIT %s OFFSET %s
                """,
                (limit, offset),
            )
            tokens = cursor.fetchall()

            return {
                "page": page,
                "limit": limit,
                "data": tokens,
            }
        finally:
            cursor.close()
            conn.close()

    def decode_refresh_token(self, refresh_token):
        """
        Decodifica um refresh token para verificar sua validade e se foi revogado.
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Verifica se o refresh_token foi revogado
            self.logger.info("Verificando se o refresh token foi revogado.")
            cursor.execute(
                "SELECT revogado FROM refresh_tokens WHERE token = %s", (refresh_token,)
            )
            result = cursor.fetchone()
            if result and result["revogado"]:
                raise ValueError("Token inválido!")

            # Decodifica o token
            return self.decode_token(refresh_token)
        except ValueError as e:
            raise ValueError(f"Erro ao decodificar refresh token: {e}")
        finally:
            cursor.close()
            conn.close()

    def revogar_refresh_token(self, refresh_token):
        """
        Revoga um refresh token específico.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Atualizar o status do refresh token para revogado
            self.logger.info("Revogando refresh token no banco.")
            cursor.execute(
                "UPDATE refresh_tokens SET revogado = TRUE WHERE token = %s",
                (refresh_token,),
            )
            if cursor.rowcount == 0:
                # Se nenhum registro foi atualizado, o token não existe ou já foi revogado
                raise ValueError("Token inválido ou já revogado!")
            conn.commit()
            self.logger.info("Refresh token revogado com sucesso.")
        except Exception as e:
            conn.rollback()
            self.logger.error("Erro ao revogar refresh token: %s", e)
            raise ValueError(f"Erro ao revogar refresh token: {e}")
        finally:
            cursor.close()
            conn.close()

    def renovar_access_token(self, refresh_token):
        """
        Renova um access_token usando um refresh_token válido.
        """
        try:
            # Decodifica o refresh_token para verificar sua validade
            decoded_refresh_token = self.decode_refresh_token(refresh_token)

            # Extrai o user_id e cargo do refresh_token
            user_id = decoded_refresh_token["user_id"]
            cargo = decoded_refresh_token.get(
                "cargo", "ADM"
            )  # Define um cargo padrão se não estiver presente

            # Gera um novo access_token
            return self.generate_access_token(user_id, cargo)
        except ValueError as e:
            self.logger.error("Erro ao renovar access_token: %s", e)
            raise ValueError(f"Erro ao renovar access_token: {e}")

    def revogar_access_token(self, access_token):
        """
        Revoga um access_token específico adicionando-o à blacklist.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Adiciona o access_token à blacklist
            self.logger.info("Adicionando access_token à blacklist.")
            cursor.execute(
                """
                INSERT INTO token_blacklist (token, invalidado_em)
                VALUES (%s, NOW())
                """,
                (access_token,),
            )
            conn.commit()
            self.logger.info("Access token revogado com sucesso.")
        except Exception as e:
            conn.rollback()
            self.logger.error("Erro ao revogar access token: %s", e)
            raise ValueError(f"Erro ao revogar access token: {e}")
        finally:
            cursor.close()
            conn.close()

    def is_token_blacklisted(self, token):
        """
        Verifica se um token está na blacklist.
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            self.logger.info("Verificando se o token está na blacklist.")
            cursor.execute("SELECT 1 FROM token_blacklist WHERE token = %s", (token,))
            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            self.logger.error("Erro ao verificar se o token está na blacklist: %s", e)
            raise ValueError(f"Erro ao verificar blacklist: {e}")
        finally:
            cursor.close()
            conn.close()
