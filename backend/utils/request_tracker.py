import os
import time
import logging
from core.config import Config

logger = logging.getLogger(__name__)


def verificar_requisicoes_diarias(Config):
    """
    Verifica se o contador diário de requisições está abaixo do limite.

    Se for um novo dia, reinicia os arquivos e retorna True.
    Caso já esteja configurado para o dia, lê o valor atual e retorna
    True se o número de requisições for menor que Config.MAX_DAILY_REQUESTS,
    ou False caso contrário.
    """
    try:
        contador_path = Config.REQUEST_TRACKER_PATH / "request_count.txt"
        data_path = Config.REQUEST_TRACKER_PATH / "request_date.txt"

        # Garante que o diretório existe
        os.makedirs(Config.REQUEST_TRACKER_PATH, exist_ok=True)

        hoje = time.strftime("%Y-%m-%d")
        if os.path.exists(data_path):
            with open(data_path, "r") as f:
                ultima_data = f.read().strip()
        else:
            ultima_data = None

        # Reinicia o contador se for um novo dia
        if ultima_data != hoje:
            with open(contador_path, "w") as f:
                f.write("0")
            with open(data_path, "w") as f:
                f.write(hoje)
            logger.info("Contador diário de requisições reiniciado.")

        # Lê o contador atual
        if os.path.exists(contador_path):
            with open(contador_path, "r") as f:
                count = int(f.read().strip())
        else:
            count = 0

        return count < Config.MAX_DAILY_REQUESTS
    except Exception as e:
        logger.error(f"Erro ao verificar requisições diárias: {e}")
        return False


def registrar_requisicao(Config):
    """
    Registra uma nova requisição no contador diário.
    """
    try:
        contador_path = Config.REQUEST_TRACKER_PATH / "request_count.txt"
        verificar_requisicoes_diarias(
            Config
        )  # Certifica-se de que o contador está inicializado

        if os.path.exists(contador_path):
            with open(contador_path, "r") as f:
                count = int(f.read().strip())
        else:
            count = 0

        count += 1

        with open(contador_path, "w") as f:
            f.write(str(count))

        logger.info(f"Requisição registrada. Total de requisições hoje: {count}")
        return count

    except Exception as e:
        logger.error(f"Erro ao registrar requisição: {e}")
        return None


def mostrar_resumo_requisicoes(Config):
    """
    Mostra o resumo das requisições diárias registradas.
    """
    try:
        contador_path = Config.REQUEST_TRACKER_PATH / "request_count.txt"

        if os.path.exists(contador_path):
            with open(contador_path, "r") as f:
                count = int(f.read().strip())
        else:
            count = 0

        logger.info(f"Resumo de requisições: Total de requisições hoje: {count}")
        return {"total_requisicoes": count}

    except Exception as e:
        logger.error(f"Erro ao mostrar resumo de requisições: {e}")
        return {"total_requisicoes": None, "erro": str(e)}
