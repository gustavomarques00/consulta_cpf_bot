import requests
from core.config import Config
from core.db import get_db_connection


class BrsmmService:
    def __init__(self):
        self.api_url = Config.BRSMM_API_URL
        self.api_key = Config.BRSMM_API_KEY

    def sync_services_to_db(self):
        """
        Sincroniza os serviços da API BRSMM com o banco de dados local.
        """
        services = self.get_services()  # Obtém os serviços da API
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            for service in services:
                cursor.execute(
                    """
                    INSERT INTO trafego_servicos (
                        brsmm_id, nome, categoria, tipo, preco_base, markup_percent, disponivel
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        nome = VALUES(nome),
                        categoria = VALUES(categoria),
                        tipo = VALUES(tipo),
                        preco_base = VALUES(preco_base),
                        markup_percent = VALUES(markup_percent),
                        disponivel = VALUES(disponivel)
                    """,
                    (
                        service["service"],  # brsmm_id
                        service["name"],  # nome
                        service.get("category", "N/A"),  # categoria
                        service.get("type", "N/A"),  # tipo
                        service["rate"],  # preco_base
                        20,  # markup_percent (exemplo fixo)
                        True,  # disponivel
                    ),
                )
            conn.commit()
            print("✅ Serviços sincronizados com sucesso.")
        except Exception as e:
            conn.rollback()
            raise Exception(f"Erro ao sincronizar serviços: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def _post(self, payload):
        payload["key"] = self.api_key
        try:
            response = requests.post(self.api_url, data=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    def get_services(self):
        return self._post({"action": "services"})

    def add_order(self, link: str, service_id: int, quantity: int):
        payload = {
            "action": "add",
            "service": service_id,
            "link": link,
            "quantity": quantity,
        }
        return self._post(payload)

    def get_order_status(self, order_id: int):
        return self._post({"action": "status", "order": order_id})

    def get_balance(self):
        return self._post({"action": "balance"})

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
