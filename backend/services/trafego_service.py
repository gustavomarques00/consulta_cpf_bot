import csv
import datetime
import os
from core.config import Config
from core.db import get_db_connection
from io import StringIO
from services.brsmm_service import BrsmmService
from datetime import datetime


class TrafegoService:
    def __init__(self):
        self.api = BrsmmService()

    def sync_servicos_brsmm(self):
        """
        Sincroniza os serviços disponíveis na API da BRSMM com o banco de dados local.
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Obtém os serviços da API
        servicos = self.api.get_services()

        if not isinstance(servicos, list):
            raise ValueError("A resposta da API não é uma lista de serviços.")

        for servico in servicos:
            # Valida se as chaves necessárias estão presentes
            if not all(
                key in servico
                for key in ["service", "name", "category", "type", "rate"]
            ):
                continue

            # Ajusta os valores para inserção no banco
            brsmm_id = servico["service"]  # Substitui 'id' por 'service'
            nome = servico["name"][:255]  # Trunca o nome para 255 caracteres
            categoria = servico["category"][:255]  # Trunca a categoria, se necessário
            tipo = servico["type"]
            preco_base = float(servico["rate"])  # Converte o preço para float
            markup_percent = 20  # Exemplo de markup padrão
            disponivel = True

            cursor.execute(
                """
                INSERT INTO trafego_servicos (
                    brsmm_id, nome, categoria, tipo, preco_base, markup_percent, disponivel
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    preco_base = VALUES(preco_base),
                    nome = VALUES(nome),
                    categoria = VALUES(categoria)
                """,
                (
                    brsmm_id,
                    nome,
                    categoria,
                    tipo,
                    preco_base,
                    markup_percent,
                    disponivel,
                ),
            )

        conn.commit()
        cursor.close()
        conn.close()

        return {"success": True, "message": "Serviços sincronizados com sucesso."}

    def enviar_pedido(self, user_id, service_id, url, quantidade):
        """
        Realiza o pedido na API da BRSMM e salva no histórico do usuário.
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Verifica se o serviço está disponível
            cursor.execute(
                "SELECT * FROM trafego_servicos WHERE brsmm_id = %s AND disponivel = TRUE",
                (service_id,),
            )
            servico = cursor.fetchone()  # Consome o resultado da consulta
            if not servico:
                return {"error": "Serviço não encontrado ou indisponível."}

            # Calcula o preço com markup
            rate_base = servico["preco_base"]
            markup = servico["markup_percent"]
            preco_unitario = round(rate_base * (1 + markup / 100), 4)
            preco_total = round(preco_unitario * quantidade, 4)

            # Faz o pedido real via API da BRSMM
            print(
                f"Enviando pedido para a API: service_id={service_id}, url={url}, quantidade={quantidade}"
            )
            brsmm_response = self.api.add_order(
                link=url, service_id=servico["brsmm_id"], quantity=quantidade
            )
            print(f"Resposta da API: {brsmm_response}")

            # Salva no histórico se o pedido foi aceito
            if "order" in brsmm_response:
                self.registrar_pedido_usuario(
                    user_id=user_id,
                    pedido_api=brsmm_response,
                    service_id=service_id,
                    url=url,
                    quantidade=quantidade,
                    preco_total=preco_total,
                )
                return {
                    "order_id": brsmm_response["order"],
                    "message": "✅ Pedido enviado com sucesso.",
                }

            return {"error": brsmm_response.get("error", "Erro desconhecido.")}
        finally:
            cursor.close()  # Fecha o cursor após consumir os resultados
            conn.close()  # Fecha a conexão

    def registrar_pedido_usuario(
        self,
        user_id,
        pedido_api,
        service_id,
        url,
        quantidade,
        preco_total,
    ):
        """
        Registra o pedido no banco de dados.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO trafego_pedidos (
                    user_id, brsmm_order_id, service_id, url, quantidade, preco_total, status, criado_em
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                """,
                (
                    user_id,
                    pedido_api.get("order"),
                    service_id,
                    url,
                    quantidade,
                    preco_total,
                    pedido_api.get("status", "Em andamento"),
                ),
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise Exception(f"Erro ao registrar pedido no banco: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def consultar_historico(self, data_param=None, status_param=None):
        """
        Consulta o histórico de envios de tráfego com base em filtros opcionais.
        """
        log_dir = os.path.join(Config.BASE_DIR, "logs", "brsmm")

        if not os.path.exists(log_dir):
            return {"message": "Nenhum log disponível ainda."}

        if data_param:
            try:
                datetime.strptime(data_param, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Data inválida. Formato esperado: YYYY-MM-DD")

            log_path = os.path.join(log_dir, f"brsmm_{data_param}.log")
            if not os.path.exists(log_path):
                raise FileNotFoundError()

            with open(log_path, "r", encoding="utf-8") as f:
                linhas = [l.strip() for l in f.readlines()]

            if status_param:
                status_param = status_param.lower()
                if status_param == "sucesso":
                    linhas = [l for l in linhas if "✅" in l]
                elif status_param == "erro":
                    linhas = [l for l in linhas if "❌" in l or "💥" in l]

            return {"data": linhas}

        historico = {}
        for nome in sorted(os.listdir(log_dir), reverse=True):
            if nome.startswith("brsmm_") and nome.endswith(".log"):
                data_log = nome.replace("brsmm_", "").replace(".log", "")
                with open(os.path.join(log_dir, nome), "r", encoding="utf-8") as f:
                    linhas = [l.strip() for l in f.readlines()]
                    if status_param:
                        if status_param == "sucesso":
                            linhas = [l for l in linhas if "✅" in l]
                        elif status_param == "erro":
                            linhas = [l for l in linhas if "❌" in l or "💥" in l]
                    historico[data_log] = linhas

        return historico

    def exportar_log_csv(self, data_param):
        """
        Exporta o log diário para um arquivo CSV.
        """
        if not data_param:
            raise ValueError("Parâmetro 'data' é obrigatório (YYYY-MM-DD)")

        try:
            datetime.strptime(data_param, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Data inválida. Formato esperado: YYYY-MM-DD")

        log_path = os.path.join(
            Config.BASE_DIR, "logs", "brsmm", f"brsmm_{data_param}.log"
        )
        if not os.path.exists(log_path):
            raise FileNotFoundError()

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["Linha"])  # Cabeçalho do CSV

        with open(log_path, "r", encoding="utf-8") as file:
            for linha in file:
                writer.writerow([linha.strip()])

        output.seek(0)
        return output

    def consultar_meus_pedidos(
        self,
        user_id,
        status=None,
        service_id=None,
        data_inicio=None,
        data_fim=None,
        page=1,
        limit=10,
    ):
        """
        Consulta os pedidos realizados pelo usuário autenticado com suporte a filtros e paginação.
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        filtros = ["user_id = %s"]  # Filtro inicial obrigatório
        params = [user_id]  # Parâmetros da query

        # Adicionar filtros dinâmicos
        if status:
            filtros.append("status = %s")
            params.append(status)

        if service_id:
            filtros.append("service_id = %s")
            params.append(service_id)

        if data_inicio:
            filtros.append("DATE(criado_em) >= %s")
            params.append(data_inicio)

        if data_fim:
            filtros.append("DATE(criado_em) <= %s")
            params.append(data_fim)

        # Construção da cláusula WHERE
        where_clause = " AND ".join(filtros)
        offset = (page - 1) * limit  # Cálculo de offset para paginação

        try:
            # Contar o total de registros que atendem aos filtros
            cursor.execute(
                f"SELECT COUNT(*) as total FROM trafego_pedidos WHERE {where_clause}",
                params,
            )
            total = cursor.fetchone()["total"]
            total_pages = (total + limit - 1) // limit  # Cálculo do total de páginas

            # Buscar os registros paginados
            cursor.execute(
                f"""
                SELECT id, brsmm_order_id, service_id, url, quantidade, preco_total, status, criado_em
                FROM trafego_pedidos
                WHERE {where_clause}
                ORDER BY criado_em DESC
                LIMIT %s OFFSET %s
                """,
                params + [limit, offset],
            )
            pedidos = cursor.fetchall()

            return {
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "total_results": total,
                "data": pedidos,
            }
        except Exception as e:
            raise Exception(f"Erro ao consultar pedidos: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def consultar_status_pedido(self, order_id, user_id):
        """
        Consulta o status de um pedido específico no banco de dados.
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT brsmm_order_id, status, quantidade, preco_total
            FROM trafego_pedidos
            WHERE id = %s AND user_id = %s
            """,
            (order_id, user_id),
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if not result:
            return {"error": "Pedido não encontrado para o usuário autenticado"}

        return result

    def consultar_status_multiplos_pedidos(self, order_ids, user_id):
        """
        Consulta o status de múltiplos pedidos no banco de dados.
        """
        if not order_ids:
            raise ValueError("É necessário passar ao menos um ID de pedido.")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Construir a query para múltiplos IDs
            placeholders = ",".join(["%s"] * len(order_ids))
            query = f"""
                SELECT brsmm_order_id, status
                FROM trafego_pedidos
                WHERE brsmm_order_id IN ({placeholders}) AND user_id = %s
            """
            cursor.execute(query, tuple(order_ids) + (user_id,))
            pedidos = cursor.fetchall()

            if not pedidos:
                return {"error": "Nenhum pedido encontrado para os IDs fornecidos."}

            # Retornar os pedidos encontrados com seus status
            return [
                {"order_id": pedido["brsmm_order_id"], "status": pedido["status"]}
                for pedido in pedidos
            ]
        except Exception as e:
            raise Exception(f"Erro ao consultar status de múltiplos pedidos: {str(e)}")
        finally:
            cursor.close()
            conn.close()
