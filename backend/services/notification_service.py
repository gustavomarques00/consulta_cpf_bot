from core.db import get_db_connection
import logging

# Configuração do Logger
logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self):
        pass

    def notificar_operador(self, chefe_id, operador_id, mensagem):
        """
        Envia uma notificação para um operador associado a um chefe de equipe.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Verificar se o operador está associado ao chefe
            logger.info(
                f"Verificando associação entre Chefe ID {chefe_id} e Operador ID {operador_id}."
            )
            cursor.execute(
                """
                SELECT 1
                FROM chefe_operadores co
                WHERE co.chefe_id = %s AND co.operador_id = %s
                """,
                (chefe_id, operador_id),
            )
            operador_valido = cursor.fetchone()

            if not operador_valido:
                logger.warning("Operador não associado ao Chefe de Equipe.")
                return {"error": "Operador não associado ao Chefe de Equipe"}, 403

            # Inserir notificação no banco de dados
            logger.info("Salvando notificação no sistema interno de mensagens.")
            cursor.execute(
                """
                INSERT INTO notificacoes (operador_id, mensagem, lida, criada_em)
                VALUES (%s, %s, FALSE, NOW())
                """,
                (operador_id, mensagem),
            )
            conn.commit()

            # Obter o ID da notificação recém-criada
            cursor.execute("SELECT LAST_INSERT_ID() AS id")
            notificacao_id = cursor.fetchone()["id"]

            logger.info("Notificação salva com sucesso no sistema interno.")
            return {
                "id": notificacao_id,
                "message": "✅ Notificação enviada com sucesso no sistema interno.",
                "operador_id": operador_id,
                "mensagem": mensagem,
            }, 200
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Erro ao salvar notificação no sistema interno: {str(e)}")
            return {
                "error": f"Erro ao salvar notificação no sistema interno: {str(e)}"
            }, 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def listar_notificacoes(self, operador_id):
        """
        Lista as notificações de um operador.
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            logger.info(f"Listando notificações para o operador {operador_id}.")
            cursor.execute(
                """
                SELECT id, mensagem, lida, criada_em
                FROM notificacoes
                WHERE operador_id = %s
                ORDER BY criada_em DESC
                """,
                (operador_id,),
            )
            notificacoes = cursor.fetchall()
            return {"notificacoes": notificacoes}, 200
        except Exception as e:
            logger.error(f"Erro ao listar notificações: {str(e)}")
            return {"error": "Erro ao listar notificações"}, 500
        finally:
            cursor.close()
            conn.close()

    def marcar_notificacao_como_lida(self, operador_id, notificacao_id):
        """
        Marca uma notificação como lida.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            logger.info(
                f"Marcando notificação {notificacao_id} como lida para operador {operador_id}."
            )
            cursor.execute(
                """
                UPDATE notificacoes
                SET lida = TRUE
                WHERE id = %s AND operador_id = %s
                """,
                (notificacao_id, operador_id),
            )
            if cursor.rowcount == 0:
                logger.warning(
                    f"Notificação {notificacao_id} não encontrada ou não pertence ao operador {operador_id}."
                )
                return {
                    "error": "Notificação não encontrada ou não pertence ao operador"
                }, 404
            conn.commit()
            return {"message": "Notificação marcada como lida"}, 200
        except Exception as e:
            logger.error(f"Erro ao marcar notificação como lida: {str(e)}")
            return {"error": "Erro interno no servidor"}, 500
        finally:
            cursor.close()
            conn.close()

    def deletar_notificacao(self, chefe_id, notificacao_id):
        """
        Deleta uma notificação específica associada a um operador do chefe.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            logger.info(
                f"Tentando deletar notificação {notificacao_id} pelo Chefe de Equipe {chefe_id}."
            )
            # Verificar se a notificação pertence a um operador associado ao chefe
            cursor.execute(
                """
                SELECT n.id
                FROM notificacoes n
                JOIN chefe_operadores co ON n.operador_id = co.operador_id
                WHERE n.id = %s AND co.chefe_id = %s
                """,
                (notificacao_id, chefe_id),
            )
            notificacao = cursor.fetchone()

            if not notificacao:
                logger.warning(
                    f"Notificação {notificacao_id} não encontrada ou não pertence ao Chefe de Equipe {chefe_id}."
                )
                return {
                    "error": "Notificação não encontrada ou não pertence ao Chefe de Equipe"
                }, 404

            # Deletar a notificação
            cursor.execute(
                """
                DELETE FROM notificacoes
                WHERE id = %s
                """,
                (notificacao_id,),
            )
            conn.commit()
            return {"message": "Notificação deletada com sucesso"}, 200
        except Exception as e:
            logger.error(f"Erro ao deletar notificação {notificacao_id}: {str(e)}")
            return {"error": "Erro interno no servidor"}, 500
        finally:
            cursor.close()
            conn.close()
