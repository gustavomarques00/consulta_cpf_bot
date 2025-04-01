import os
import json
import time
from datetime import datetime, timedelta
from utils.emoji import EMOJI
from backend.core.config import Config


# =============================
# 📊 Verificação de requisições diárias
# =============================
def verificar_requisicoes_diarias(Config):
    try:
        hoje = time.strftime("%Y-%m-%d")
        contador_path = Config.REQUEST_TRACKER_PATH / "request_count.txt"
        data_path = Config.REQUEST_TRACKER_PATH / "request_date.txt"

        # Garante que o diretório exista
        os.makedirs(Config.REQUEST_TRACKER_PATH, exist_ok=True)

        if os.path.exists(data_path):
            with open(data_path, "r") as f:
                ultima_data = f.read().strip()
        else:
            ultima_data = ""

        if ultima_data != hoje:
            with open(contador_path, "w") as f:
                f.write("0")
            with open(data_path, "w") as f:
                f.write(hoje)

        if os.path.exists(contador_path):
            with open(contador_path, "r") as f:
                count = int(f.read().strip())
        else:
            count = 0

        if count >= Config.MAX_DAILY_REQUESTS:
            print(f"{EMOJI['warn']} Limite diário de requisições atingido.")
            return False

        return True

    except Exception as e:
        print(f"{EMOJI['error']} Erro ao verificar limite de requisições: {e}")
        return False


# =============================
# 📝 Registro de cada requisição
# =============================
def registrar_requisicao():
    try:
        contador_path = Config.REQUEST_TRACKER_PATH / "request_count.txt"
        log_path = Config.REQUEST_TRACKER_PATH / "request_log.json"

        os.makedirs(Config.REQUEST_TRACKER_PATH, exist_ok=True)

        if os.path.exists(contador_path):
            with open(contador_path, "r") as file:
                count = int(file.read().strip())
        else:
            count = 0

        count += 1
        with open(contador_path, "w") as file:
            file.write(str(count))

        now = datetime.now().isoformat()

        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                logs = json.load(f)
        else:
            logs = []

        logs.append(now)
        with open(log_path, "w") as f:
            json.dump(logs, f, indent=2)

    except Exception as e:
        print(f"{EMOJI['error']} Erro ao registrar requisição: {e}")


# =============================
# 📈 Exibe o resumo de requisições
# =============================
def mostrar_resumo_requisicoes():
    try:
        log_path = Config.REQUEST_TRACKER_PATH / "request_log.json"

        if not os.path.exists(log_path):
            print(f"{EMOJI['info']} Nenhum log de requisição encontrado.")
            return

        with open(log_path, "r") as f:
            logs = json.load(f)

        datas = [datetime.fromisoformat(log) for log in logs]
        hoje = datetime.now()
        sete_dias = hoje - timedelta(days=7)
        quinze_dias = hoje - timedelta(days=15)

        total_hoje = sum(1 for d in datas if d.date() == hoje.date())
        total_7 = sum(1 for d in datas if d >= sete_dias)
        total_15 = sum(1 for d in datas if d >= quinze_dias)
        total_mes = sum(
            1 for d in datas if d.month == hoje.month and d.year == hoje.year
        )

        print("\n📈 Resumo de Requisições:")
        print(f"📅 Hoje: {total_hoje}")
        print(f"📆 Últimos 7 dias: {total_7}")
        print(f"🗓️ Últimos 15 dias: {total_15}")
        print(f"🗓️ Mês atual: {total_mes}\n")

    except Exception as e:
        print(f"{EMOJI['error']} Erro ao exibir resumo de requisições: {e}")
