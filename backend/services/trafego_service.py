from services.brsmm_service import BrsmmService
from backend.core.db import get_db_connection

class TrafegoService:
    def __init__(self):
        self.api = BrsmmService()

    def sync_servicos_brsmm(self):
        """
        Consulta os serviços disponíveis na BRSMM e salva localmente com markup padrão.
        """
        servicos = self.api.get_services()

        conn = get_db_connection()
        cursor = conn.cursor()

        for s in servicos:
            cursor.execute("""
                INSERT INTO trafego_servicos (brsmm_id, nome, categoria, tipo, preco_base, markup_percent)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE preco_base = VALUES(preco_base), nome = VALUES(nome), categoria = VALUES(categoria)
            """, (
                s["service"],
                s["name"],
                s.get("category", ""),
                s.get("type", ""),
                float(s["rate"]),
                50.0
            ))

        conn.commit()
        cursor.close()
        conn.close()
        return {"success": True, "total_importados": len(servicos)}

    def enviar_pedido(self, user_id, service_id, url, quantidade):
        """
        Realiza o pedido na BRSMM e retorna o custo com markup.
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM trafego_servicos WHERE id = %s AND disponivel = TRUE", (service_id,))
        servico = cursor.fetchone()
        cursor.close()
        conn.close()

        if not servico:
            return {"error": "Serviço não encontrado ou indisponível."}

        rate_base = servico["preco_base"]
        markup = servico["markup_percent"]
        preco_unitario = round(rate_base * (1 + markup / 100), 4)
        preco_total = round(preco_unitario * quantidade, 4)

        # Envia pedido via API real
        brsmm_response = self.api.add_order(
            link=url,
            service_id=servico["brsmm_id"],
            quantity=quantidade
        )

        return {
            "pedido_api": brsmm_response,
            "preco_total": preco_total,
            "markup_percent": markup,
            "preco_unitario": preco_unitario
        }
