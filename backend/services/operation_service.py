import datetime
import json
from core.config import Config
from core.db import get_db_connection
from services.extracao_service import ExtracaoService
from utils.validators import validar_formato_cpf
import logging

logger = logging.getLogger(__name__)


class OperationService:
    def listar_operadores(self, chefe_id):
        """
        Lista os operadores associados ao Chefe de Equipe autenticado.
        """
        logger.info("Iniciando listagem de operadores para chefe_id=%s", chefe_id)
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            logger.debug(
                "Executando consulta para listar operadores associados ao chefe_id=%s",
                chefe_id,
            )
            cursor.execute(
                """
                SELECT u.id, u.nome, u.email
                FROM chefe_operadores co
                JOIN usuarios u ON co.operador_id = u.id
                WHERE co.chefe_id = %s
                """,
                (chefe_id,),
            )
            operadores = cursor.fetchall()
            logger.info(
                "Listagem de operadores concluída com sucesso para chefe_id=%s",
                chefe_id,
            )
            return operadores
        except Exception as e:
            logger.error(
                "Erro ao listar operadores para chefe_id=%s: %s",
                chefe_id,
                str(e),
                exc_info=True,
            )
            raise Exception(f"Erro ao listar operadores: {str(e)}")
        finally:
            cursor.close()
            conn.close()
            logger.debug("Conexão com o banco de dados encerrada.")

    def distribuir_dados(self, chefe_id, operador_id, quantidade_dados):
        """
        Permite ao Chefe de Equipe distribuir dados para um Operador.
        """
        logger.info(
            "Iniciando distribuição de dados: chefe_id=%s, operador_id=%s, quantidade_dados=%s",
            chefe_id,
            operador_id,
            quantidade_dados,
        )

        if quantidade_dados <= 0:
            logger.error("A quantidade de dados deve ser um número positivo.")
            raise ValueError("A quantidade de dados deve ser um número positivo.")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Verifica se o Operador pertence ao Chefe de Equipe
            logger.debug("Verificando se o Operador pertence ao Chefe de Equipe.")
            cursor.execute(
                "SELECT 1 FROM chefe_operadores WHERE chefe_id = %s AND operador_id = %s",
                (chefe_id, operador_id),
            )
            if not cursor.fetchone():
                logger.warning(
                    "Operador não associado ao Chefe de Equipe: operador_id=%s",
                    operador_id,
                )
                raise PermissionError("Operador não associado ao Chefe de Equipe.")

            # Verifica o total de dados já distribuídos ao operador
            logger.debug("Verificando o total de dados já distribuídos ao operador.")
            cursor.execute(
                """
                SELECT SUM(dados_restantes) as total_restante
                FROM distribuicao_dados
                WHERE operador_id = %s
                """,
                (operador_id,),
            )
            resultado = cursor.fetchone()
            total_atual = (
                resultado["total_restante"]
                if resultado and resultado["total_restante"]
                else 0
            )
            logger.info(
                "Total atual de dados pendentes para operador_id=%s: %s",
                operador_id,
                total_atual,
            )

            # Verifica se o total com a nova distribuição não excede o limite por operador
            limite_por_operador = (
                5000  # Limite máximo de dados não processados por operador
            )
            if total_atual + quantidade_dados > limite_por_operador:
                logger.error(
                    "Limite excedido para operador_id=%s. Total atual: %s, Tentativa de adicionar: %s, Limite máximo: %s",
                    operador_id,
                    total_atual,
                    quantidade_dados,
                    limite_por_operador,
                )
                raise ValueError(
                    f"Limite excedido. O operador já possui {total_atual} dados pendentes. "
                    f"Limite máximo: {limite_por_operador}."
                )

            # Insere ou atualiza a distribuição de dados
            logger.debug(
                "Inserindo ou atualizando a distribuição de dados para operador_id=%s.",
                operador_id,
            )
            cursor.execute(
                """
                INSERT INTO distribuicao_dados (chefe_id, operador_id, dados_distribuidos, dados_restantes, data_distribuicao)
                VALUES (%s, %s, %s, %s, NOW())
                ON DUPLICATE KEY UPDATE
                dados_distribuidos = dados_distribuidos + VALUES(dados_distribuidos),
                dados_restantes = dados_restantes + VALUES(dados_restantes)
                """,
                (chefe_id, operador_id, quantidade_dados, quantidade_dados),
            )
            conn.commit()
            logger.info(
                "Distribuição de dados concluída com sucesso para operador_id=%s.",
                operador_id,
            )
        except Exception as e:
            logger.error("Erro ao distribuir dados: %s", str(e), exc_info=True)
            conn.rollback()
            raise Exception(f"Erro ao distribuir dados: {str(e)}")
        finally:
            cursor.close()
            conn.close()
            logger.debug("Conexão com o banco de dados encerrada.")

    def progresso_operadores(self, chefe_id):
        """
        Retorna o progresso de cada Operador (dados processados/restantes).
        """
        logger.info(
            "Iniciando consulta de progresso dos operadores para chefe_id=%s", chefe_id
        )
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            logger.debug("Executando consulta para obter progresso dos operadores.")
            cursor.execute(
                """
                SELECT u.id AS operador_id, u.nome, dd.dados_distribuidos, dd.dados_restantes
                FROM distribuicao_dados dd
                JOIN usuarios u ON dd.operador_id = u.id
                WHERE dd.chefe_id = %s
                """,
                (chefe_id,),
            )
            progresso = cursor.fetchall()
            logger.info(
                "Consulta de progresso dos operadores concluída com sucesso para chefe_id=%s",
                chefe_id,
            )
            return progresso
        except Exception as e:
            logger.error(
                "Erro ao consultar progresso dos operadores para chefe_id=%s: %s",
                chefe_id,
                str(e),
                exc_info=True,
            )
            raise Exception(f"Erro ao consultar progresso dos operadores: {str(e)}")
        finally:
            cursor.close()
            conn.close()
            logger.debug("Conexão com o banco de dados encerrada.")

    def gerar_relatorio_desempenho(self, chefe_id, periodo, operador_id=None):
        """
        Gera um relatório detalhado do desempenho dos operadores associados ao Chefe de Equipe.
        """
        logger.info(
            "Iniciando geração do relatório de desempenho para chefe_id=%s, periodo=%s, operador_id=%s",
            chefe_id,
            periodo,
            operador_id,
        )
        hoje = datetime.datetime.now().date()

        try:
            # Definir intervalo de datas baseado no período
            if periodo == "hoje":
                data_inicio = hoje
                data_fim = hoje
            elif periodo == "mes":
                data_inicio = datetime.datetime(hoje.year, hoje.month, 1).date()
                if hoje.month == 12:
                    data_fim = datetime.datetime(
                        hoje.year + 1, 1, 1
                    ).date() - datetime.timedelta(days=1)
                else:
                    data_fim = datetime.datetime(
                        hoje.year, hoje.month + 1, 1
                    ).date() - datetime.timedelta(days=1)
            else:  # semana (padrão)
                data_inicio = hoje - datetime.timedelta(days=hoje.weekday())
                data_fim = data_inicio + datetime.timedelta(days=6)

            logger.debug(
                "Intervalo de datas definido: data_inicio=%s, data_fim=%s",
                data_inicio,
                data_fim,
            )

            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Filtro de operador específico, se fornecido
            operador_filter = ""
            params = [chefe_id]
            if operador_id:
                operador_filter = " AND dd.operador_id = %s"
                params.append(operador_id)

            # Consulta para obter dados de desempenho
            query = f"""
            SELECT 
                u.id AS operador_id, 
                u.nome, 
                u.email,
                dd.dados_distribuidos,
                dd.dados_restantes,
                (dd.dados_distribuidos - dd.dados_restantes) AS dados_processados,
                CASE 
                    WHEN dd.dados_distribuidos > 0 
                    THEN ((dd.dados_distribuidos - dd.dados_restantes) / dd.dados_distribuidos * 100) 
                    ELSE 0 
                END AS eficiencia,
                (
                    SELECT AVG(TIMESTAMPDIFF(MINUTE, hr.inicio, hr.fim))
                    FROM historico_registros hr
                    WHERE hr.operador_id = u.id 
                    AND DATE(hr.data_registro) BETWEEN %s AND %s
                ) AS tempo_medio_minutos
            FROM distribuicao_dados dd
            JOIN usuarios u ON dd.operador_id = u.id
            WHERE dd.chefe_id = %s{operador_filter}
            """
            logger.debug(
                "Executando consulta principal para obter dados de desempenho."
            )
            cursor.execute(query, [data_inicio, data_fim] + params)
            resultados = cursor.fetchall()
            logger.info(
                "Consulta principal executada com sucesso. Resultados obtidos: %d operadores.",
                len(resultados),
            )

            # Para cada operador, buscar detalhes diários
            for operador in resultados:
                logger.debug(
                    "Buscando detalhes diários para operador_id=%s",
                    operador["operador_id"],
                )
                cursor.execute(
                    """
                    SELECT 
                        DATE(hr.data_registro) AS data,
                        COUNT(hr.id) AS registros_processados,
                        SEC_TO_TIME(AVG(TIMESTAMPDIFF(SECOND, hr.inicio, hr.fim))) AS tempo_medio
                    FROM historico_registros hr
                    WHERE hr.operador_id = %s
                    AND DATE(hr.data_registro) BETWEEN %s AND %s
                    GROUP BY DATE(hr.data_registro)
                    ORDER BY data
                    """,
                    [operador["operador_id"], data_inicio, data_fim],
                )

                detalhes_diarios = cursor.fetchall()
                operador["detalhes_diarios"] = detalhes_diarios
                logger.debug(
                    "Detalhes diários obtidos para operador_id=%s: %s",
                    operador["operador_id"],
                    detalhes_diarios,
                )

                # Converter para formato HH:MM:SS
                if operador["tempo_medio_minutos"]:
                    horas = int(operador["tempo_medio_minutos"] // 60)
                    minutos = int(operador["tempo_medio_minutos"] % 60)
                    operador["tempo_medio_processamento"] = (
                        f"{horas:02d}:{minutos:02d}:00"
                    )
                else:
                    operador["tempo_medio_processamento"] = "00:00:00"

                # Remover campo temporário
                del operador["tempo_medio_minutos"]

            logger.info(
                "Relatório de desempenho gerado com sucesso para chefe_id=%s", chefe_id
            )
            return {
                "periodo": periodo,
                "data_inicio": data_inicio.strftime("%Y-%m-%d"),
                "data_fim": data_fim.strftime("%Y-%m-%d"),
                "desempenho": resultados,
            }
        except Exception as e:
            logger.error(
                "Erro ao gerar relatório de desempenho para chefe_id=%s: %s",
                chefe_id,
                str(e),
                exc_info=True,
            )
            raise Exception(f"Erro ao gerar relatório de desempenho: {str(e)}")
        finally:
            if "cursor" in locals():
                cursor.close()
            if "conn" in locals():
                conn.close()
            logger.debug("Conexão com o banco de dados encerrada.")

    def obter_historico_distribuicao(self, chefe_id):
        """
        Obtém o histórico de distribuições realizadas pelo Chefe de Equipe para seus Operadores.
        """
        logger.info(
            "Iniciando obtenção do histórico de distribuições para chefe_id=%s",
            chefe_id,
        )
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            logger.debug("Executando consulta para obter o histórico de distribuições.")
            # Consulta para obter o histórico de distribuições
            cursor.execute(
                """
                SELECT 
                    dd.data_distribuicao,
                    u.id AS operador_id,
                    u.nome AS nome_operador,
                    dd.dados_distribuidos
                FROM distribuicao_dados dd
                JOIN usuarios u ON dd.operador_id = u.id
                WHERE dd.chefe_id = %s
                ORDER BY dd.data_distribuicao DESC
                """,
                (chefe_id,),
            )
            historico = cursor.fetchall()
            logger.info(
                "Histórico de distribuições obtido com sucesso para chefe_id=%s",
                chefe_id,
            )
            return historico
        except Exception as e:
            logger.error(
                "Erro ao obter histórico de distribuição para chefe_id=%s: %s",
                chefe_id,
                str(e),
                exc_info=True,
            )
            raise Exception(f"Erro ao obter histórico de distribuição: {str(e)}")
        finally:
            cursor.close()
            conn.close()
            logger.debug("Conexão com o banco de dados encerrada.")

    def reatribuir_dados(
        self, chefe_id, operador_origem_id, operador_destino_id, quantidade_dados
    ):
        """
        Reatribui dados não processados de um Operador para outro.
        """
        if quantidade_dados <= 0:
            logger.error("A quantidade de dados deve ser um número positivo.")
            raise ValueError("A quantidade de dados deve ser um número positivo.")

        if operador_origem_id == operador_destino_id:
            logger.error("O operador de origem e destino não podem ser o mesmo.")
            raise ValueError("O operador de origem e destino não podem ser o mesmo.")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            logger.info(
                "Iniciando reatribuição de dados: chefe_id=%s, operador_origem_id=%s, operador_destino_id=%s, quantidade_dados=%s",
                chefe_id,
                operador_origem_id,
                operador_destino_id,
                quantidade_dados,
            )

            # Verifica se o Operador de origem pertence ao Chefe de Equipe
            logger.debug(
                "Verificando se o Operador de origem pertence ao Chefe de Equipe."
            )
            cursor.execute(
                "SELECT 1 FROM chefe_operadores WHERE chefe_id = %s AND operador_id = %s",
                (chefe_id, operador_origem_id),
            )
            if not cursor.fetchone():
                logger.warning(
                    "Operador de origem não pertence ao Chefe de Equipe: operador_origem_id=%s",
                    operador_origem_id,
                )
                raise PermissionError(
                    "O Operador de origem não pertence ao Chefe de Equipe."
                )

            # Verifica se o Operador de destino pertence ao Chefe de Equipe
            logger.debug(
                "Verificando se o Operador de destino pertence ao Chefe de Equipe."
            )
            cursor.execute(
                "SELECT 1 FROM chefe_operadores WHERE chefe_id = %s AND operador_id = %s",
                (chefe_id, operador_destino_id),
            )
            if not cursor.fetchone():
                logger.warning(
                    "Operador de destino não pertence ao Chefe de Equipe: operador_destino_id=%s",
                    operador_destino_id,
                )
                raise PermissionError(
                    "O Operador de destino não pertence ao Chefe de Equipe."
                )

            # Verifica se o Operador de origem tem dados suficientes
            logger.debug(
                "Verificando se o Operador de origem possui dados suficientes."
            )
            cursor.execute(
                "SELECT dados_restantes FROM distribuicao_dados WHERE operador_id = %s",
                (operador_origem_id,),
            )
            origem_dados = cursor.fetchone()
            if not origem_dados or origem_dados["dados_restantes"] < quantidade_dados:
                logger.warning(
                    "Operador de origem não possui dados suficientes: operador_origem_id=%s, dados_restantes=%s",
                    operador_origem_id,
                    origem_dados["dados_restantes"] if origem_dados else 0,
                )
                raise ValueError("O Operador de origem não possui dados suficientes.")

            # Atualiza os dados dos Operadores
            logger.debug("Atualizando dados do Operador de origem.")
            cursor.execute(
                "UPDATE distribuicao_dados SET dados_restantes = dados_restantes - %s WHERE operador_id = %s",
                (quantidade_dados, operador_origem_id),
            )
            logger.debug("Atualizando dados do Operador de destino.")
            cursor.execute(
                "UPDATE distribuicao_dados SET dados_restantes = dados_restantes + %s WHERE operador_id = %s",
                (quantidade_dados, operador_destino_id),
            )
            conn.commit()
            logger.info(
                "Reatribuição de dados concluída com sucesso: operador_origem_id=%s, operador_destino_id=%s, quantidade_dados=%s",
                operador_origem_id,
                operador_destino_id,
                quantidade_dados,
            )
        except Exception as e:
            logger.error("Erro ao reatribuir dados: %s", str(e), exc_info=True)
            conn.rollback()
            raise Exception(f"Erro ao reatribuir dados: {str(e)}")
        finally:
            cursor.close()
            conn.close()
            logger.debug("Conexão com o banco de dados encerrada.")

    def processar_cpfs_upload(
        self, chefe_id, cpfs, campos_desejados, status_inicial="Criar"
    ):
        """
        Processa uma lista de CPFs enviados pelo Chefe de Equipe e retorna os resultados.
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            logger.info("Iniciando processamento de CPFs para chefe_id=%s", chefe_id)
            resultados = []

            # Cria uma instância de ExtracaoService
            extracao_service = ExtracaoService(Config)

            for cpf in cpfs:
                logger.debug("Processando CPF: %s", cpf)

                # Valida o formato do CPF
                if not validar_formato_cpf(cpf):
                    logger.warning("CPF inválido: %s", cpf)
                    resultados.append({"cpf": cpf, "status": "Formato Inválido"})
                    continue

                # Verifica se o CPF já foi processado
                cursor.execute(
                    """
                    SELECT 1 FROM historico_processamento
                    WHERE chefe_id = %s AND cpf = %s
                    """,
                    (chefe_id, cpf),
                )
                if cursor.fetchone():
                    logger.info("CPF já processado: %s", cpf)
                    resultados.append({"cpf": cpf, "status": "Já Processado"})
                    continue

                # Consulta a API para obter os dados do CPF
                logger.debug("Consultando API para CPF: %s", cpf)
                dados = extracao_service.consultar_api(
                    cpf
                )  # Usa a instância corretamente
                if not dados:
                    logger.warning("Nenhum dado encontrado para CPF: %s", cpf)
                    resultados.append({"cpf": cpf, "status": "Nenhum dado encontrado"})
                    continue

                # Filtra os dados com base nos campos desejados
                logger.debug("Filtrando dados para CPF: %s", cpf)
                dados_filtrados = extracao_service.filtrar_dados_api(
                    dados, campos_desejados
                )
                dados_filtrados["cpf"] = cpf
                dados_filtrados["status"] = status_inicial

                # Adiciona o resultado à lista
                resultados.append(dados_filtrados)

                # Registra o processamento no banco de dados
                logger.debug("Registrando processamento no banco para CPF: %s", cpf)
                cursor.execute(
                    """
                    INSERT INTO historico_processamento (chefe_id, cpf, dados, status, data_processamento)
                    VALUES (%s, %s, %s, %s, NOW())
                    """,
                    (
                        chefe_id,
                        cpf,
                        json.dumps(
                            dados_filtrados
                        ),  # Salva os dados filtrados como JSON
                        status_inicial,
                    ),
                )
                conn.commit()

            logger.info("Processamento de CPFs concluído para chefe_id=%s", chefe_id)
            return resultados

        except Exception as e:
            logger.error("Erro ao processar CPFs: %s", str(e), exc_info=True)
            conn.rollback()
            raise Exception(f"Erro ao processar CPFs: {str(e)}")
        finally:
            cursor.close()
            conn.close()
            logger.debug("Conexão com o banco de dados encerrada.")
