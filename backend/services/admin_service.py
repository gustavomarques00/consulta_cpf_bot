from core.db import get_db_connection
import logging

# Configuração do Logger
logger = logging.getLogger(__name__)


class AdminService:
    def listar_refresh_tokens(
        self, page, limit, email_filter=None, revogado_filter=None
    ):
        """
        Lista todos os refresh tokens com paginação e filtros opcionais.

        Args:
            page (int): Número da página.
            limit (int): Limite de itens por página.
            email_filter (str, optional): Filtro pelo email do usuário.
            revogado_filter (str, optional): Filtro pelo status de revogação.

        Returns:
            dict: Dados paginados dos tokens.
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Construção da query com filtros opcionais
            query = """
                SELECT rt.id, rt.token, rt.revogado, rt.criado_em, rt.expira_em, u.email AS usuario_email
                FROM refresh_tokens rt
                JOIN usuarios u ON rt.usuario_id = u.id
                WHERE 1=1
            """
            params = []

            if email_filter:
                query += " AND u.email LIKE %s"
                params.append(f"%{email_filter}%")

            if revogado_filter is not None:
                query += " AND rt.revogado = %s"
                params.append(revogado_filter.lower() == "true")

            # Paginação
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, (page - 1) * limit])

            cursor.execute(query, tuple(params))
            tokens = cursor.fetchall()

            # Total de resultados
            cursor.execute(
                "SELECT COUNT(*) FROM refresh_tokens rt JOIN usuarios u ON rt.usuario_id = u.id WHERE 1=1"
            )
            total_results = cursor.fetchone()[0]

            total_pages = (total_results + limit - 1) // limit

            return {
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "total_results": total_results,
                "data": [
                    {
                        "id": token[0],
                        "token": token[1],
                        "revogado": token[2],
                        "criado_em": token[3],
                        "expira_em": token[4],
                        "usuario_email": token[5],
                    }
                    for token in tokens
                ],
            }
        except Exception as e:
            logger.error(f"Erro ao listar refresh tokens: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def listar_tokens_revogados(self, page, limit):
        """
        Lista tokens de access revogados com paginação.

        Args:
            page (int): Número da página.
            limit (int): Limite de itens por página.

        Returns:
            dict: Dados paginados dos tokens revogados.
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Query para listar tokens revogados
            query = """
                SELECT id, token, invalidado_em
                FROM access_tokens_blacklist
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (limit, (page - 1) * limit))
            tokens = cursor.fetchall()

            # Total de resultados
            cursor.execute("SELECT COUNT(*) FROM access_tokens_blacklist")
            total_results = cursor.fetchone()[0]

            total_pages = (total_results + limit - 1) // limit

            return {
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "total_results": total_results,
                "data": [
                    {
                        "id": token[0],
                        "token": token[1],
                        "invalidado_em": token[2],
                    }
                    for token in tokens
                ],
            }
        except Exception as e:
            logger.error(f"Erro ao listar tokens revogados: {e}")
            raise
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
            # Atualizar o status do refresh token
            logger.info("Revogando refresh token no banco.")
            cursor.execute(
                "UPDATE refresh_tokens SET revogado = TRUE WHERE token = %s",
                (refresh_token,),
            )
            if cursor.rowcount == 0:
                # Se nenhum registro foi atualizado, o token não existe ou já foi revogado
                raise ValueError("Token inválido ou já revogado!")
            conn.commit()
            logger.info("Refresh token revogado com sucesso.")
        except Exception as e:
            conn.rollback()
            logger.error("Erro ao revogar refresh token: %s", e)
            raise ValueError(f"Erro ao revogar refresh token: {e}")
        finally:
            cursor.close()
            conn.close()

    def gerar_token(self, user_id, cargo):
        """
        Gera e armazena um token JWT vinculado ao usuário e plano.

        Args:
            user_id (int): ID do usuário.
            cargo (str): Cargo do usuário.

        Returns:
            dict: Tokens gerados (access_token e refresh_token).

        Raises:
            ValueError: Se o plano do usuário não for encontrado.
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Verifica se o usuário possui um plano
            cursor.execute(
                "SELECT plano_id FROM usuarios_planos WHERE usuario_id = %s", (user_id,)
            )
            user_plan = cursor.fetchone()
            if not user_plan:
                raise ValueError("Plano não encontrado!")

            # Gera os tokens (substitua pela lógica de geração de tokens)
            access_token = f"access_token_{user_id}"
            refresh_token = f"refresh_token_{user_id}"

            # Armazena os tokens no banco
            cursor.execute(
                """
                INSERT INTO refresh_tokens (token, usuario_id, revogado, criado_em, expira_em)
                VALUES (%s, %s, FALSE, NOW(), DATE_ADD(NOW(), INTERVAL 7 DAY))
                """,
                (refresh_token, user_id),
            )
            conn.commit()

            return {"access_token": access_token, "refresh_token": refresh_token}
        except Exception as e:
            logger.error(f"Erro ao gerar token: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
