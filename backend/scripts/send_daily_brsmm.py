import sys
import os
import random
from datetime import datetime

# Garante que os imports absolutos funcionem
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.brsmm_service import BrsmmService

# 🎯 URLs fixas e ID do serviço
URLS_DIARIAS = [
    "https://apretailer.com.br/click/67c140362bfa8136ea48f2f9/185510/349334/subaccount",
    "https://apretailer.com.br/click/67d4bfd92bfa815c42685e06/185510/351953/subaccount",
]

SERVICE_ID = 171
QUANTIDADE_MIN = 900
QUANTIDADE_MAX = 1250

# 📂 Pasta de logs
LOG_DIR = os.path.join("logs", "brsmm")
os.makedirs(LOG_DIR, exist_ok=True)


def logar(mensagem, arquivo_log):
    """Escreve no log e imprime no terminal"""
    print(mensagem)
    arquivo_log.write(mensagem + "\n")


def enviar_pedidos():
    api = BrsmmService()
    now = datetime.now()
    log_path = os.path.join(LOG_DIR, f"brsmm_{now.strftime('%Y-%m-%d')}.log")

    with open(log_path, "a", encoding="utf-8") as log:
        logar(f"\n🕕 Execução iniciada em: {now.strftime('%Y-%m-%d %H:%M:%S')}", log)

        # 💰 Consulta saldo
        saldo = api.get_balance()
        saldo_float = float(saldo.get("balance", 0))
        logar(f"💰 Saldo atual: ${saldo_float:.2f} USD", log)

        # 📦 Busca informações do serviço
        services = api.get_services()
        selected = next((s for s in services if s["service"] == SERVICE_ID), None)
        if not selected:
            logar(f"❌ Serviço {SERVICE_ID} não encontrado!", log)
            return

        rate = float(selected["rate"])
        logar(f"📦 Serviço: {selected['name']} | Rate: ${rate:.4f}", log)

        total_gasto = 0

        for url in URLS_DIARIAS:
            quantidade = random.randint(QUANTIDADE_MIN, QUANTIDADE_MAX)
            custo_estimado = round(rate * quantidade, 4)
            total_gasto += custo_estimado

            logar(
                f"➡️ Enviando tráfego para {url}\n   • Quantidade: {quantidade} | 💸 Estimado: ${custo_estimado}",
                log,
            )

            try:
                response = api.add_order(
                    link=url, service_id=SERVICE_ID, quantity=quantidade
                )
                if "order" in response:
                    logar(f"✅ Pedido criado com sucesso! ID: {response['order']}", log)
                else:
                    logar(f"❌ Erro no envio: {response}", log)
            except Exception as e:
                logar(f"💥 Erro inesperado: {str(e)}", log)

        logar(f"📊 Total estimado gasto nesta execução: ${total_gasto:.4f}", log)
        logar(f"📊 Saldo atual: ${saldo_float:.2f}", log)
        logar("🏁 Execução finalizada.\n", log)


if __name__ == "__main__":
    enviar_pedidos()
