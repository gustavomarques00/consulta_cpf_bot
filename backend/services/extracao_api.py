import requests
import time
import random
from utils.emoji import EMOJI
from utils.request_tracker import registrar_requisicao


def consultar_api(cpf, Config, attempt=1, sheet_checker=None, reagendar_func=None):
    if not registrar_requisicao:
        return None

    url = f"{Config.API_URL}?token={Config.API_TOKEN}&cpf={cpf}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        registrar_requisicao()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"{EMOJI['error']} Erro na consulta da API (CPF {cpf}): {e}")
        if attempt < Config.MAX_RETRIES:
            wait = Config.RETRY_DELAY * (2 ** (attempt - 1)) + random.uniform(1, 2)
            print(
                f"{EMOJI['loop']} Tentativa {attempt} falhou. Retentando em {wait:.2f}s..."
            )
            time.sleep(wait)
            return consultar_api(
                cpf, Config, attempt + 1, sheet_checker, reagendar_func
            )
        else:
            print(f"{EMOJI['warn']} Máximo de tentativas atingido para CPF {cpf}.")
            if sheet_checker and reagendar_func:
                reagendar_func(sheet_checker, cpf)
            return None


def tratar_valor(valor):
    if not valor or str(valor).strip().upper() in ["", "SEM INFORMAÇÃO", "N/A"]:
        return "Não Informado"
    return str(valor).strip()
