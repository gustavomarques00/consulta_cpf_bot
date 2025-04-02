import requests
from core.config import Config
from core.db import get_db_connection


class BrsmmService:
    def __init__(self):
        self.api_url = Config.BRSMM_API_URL
        self.api_key = Config.BRSMM_API_KEY

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

    @staticmethod
    def registrar_pedido_usuario(
        user_id, pedido_api, service_id, url, quantidade, preco_unitario, preco_total
    ):
        """
        Registra o pedido no banco de dados, associando ao usuário autenticado.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO trafego_pedidos (
                    user_id, brsmm_order_id, service_id, url,
                    quantidade, preco_unitario, preco_total, status, criado_em
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """,
                (
                    user_id,
                    pedido_api.get("order"),
                    service_id,
                    url,
                    quantidade,
                    preco_unitario,
                    preco_total,
                    pedido_api.get("status", "Pendente"),
                ),
            )
            conn.commit()
            print(f"✅ Pedido do usuário {user_id} registrado com sucesso.")
        except Exception as e:
            print(f"❌ Erro ao registrar pedido no banco: {e}")
        finally:
            cursor.close()
            conn.close()
