import requests
import time
import random
import logging
from utils.emoji import EMOJI
from utils.request_tracker import registrar_requisicao

# Configuração do Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExtracaoService:
    def __init__(self, config):
        self.config = config
        self.CAMPOS_PERMITIDOS = [
            "NOME",
            "CPF",
            "SEXO",
            "NASCIMENTO",
            "RENDA",
            "PODER_AQUISITIVO",
            "EMAIL",
            "TELEFONES",
        ]
        self.VALOR_PADRAO = "Não Informado"

    def consultar_api(self, cpf, attempt=1, sheet_checker=None, reagendar_func=None):
        """
        Consulta a API para obter informações de um CPF.
        """
        if not registrar_requisicao:
            return None

        url = f"{self.config.API_URL}?token={self.config.API_TOKEN}&cpf={cpf}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            registrar_requisicao(self.config)
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"{EMOJI['error']} Erro na consulta da API (CPF {cpf}): {e}")
            if attempt < self.config.MAX_RETRIES:
                wait = self.config.RETRY_DELAY * (2 ** (attempt - 1)) + random.uniform(
                    1, 2
                )
                logger.warning(
                    f"{EMOJI['loop']} Tentativa {attempt} falhou. Retentando em {wait:.2f}s..."
                )
                time.sleep(wait)
                return self.consultar_api(
                    cpf, attempt + 1, sheet_checker, reagendar_func
                )
            else:
                logger.warning(
                    f"{EMOJI['warn']} Máximo de tentativas atingido para CPF {cpf}."
                )
                if sheet_checker and reagendar_func:
                    reagendar_func(sheet_checker, cpf)
                return None

    def tratar_valor(self, valor):
        """
        Trata valores ausentes ou inválidos, retornando um valor padrão.
        """
        if not valor or str(valor).strip().upper() in ["", "SEM INFORMAÇÃO", "N/A"]:
            return self.VALOR_PADRAO
        return str(valor).strip()

    def filtrar_dados_api(self, dados: dict, campos_desejados: list) -> dict:
        """
        Filtra os dados retornados pela API com base nos campos desejados.
        """
        logger.info(
            f"Iniciando filtragem dos dados da API. Total de campos desejados: {len(campos_desejados)}."
        )
        dados_filtrados = {}

        for campo in campos_desejados:
            logger.info(f"Processando campo: {campo}")

            # Tratamento especial para TELEFONES
            if campo == "TELEFONES":
                telefones = dados.get("TELEFONES", [])
                logger.info(f"Telefones encontrados: {telefones}")
                if telefones:
                    primeiro = telefones[0].get("NUMBER", self.VALOR_PADRAO)
                    dados_filtrados["TELEFONES"] = self.tratar_valor(primeiro)
                    logger.info(f"Campo 'TELEFONES' tratado: {dados_filtrados['TELEFONES']}")
                else:
                    dados_filtrados["TELEFONES"] = self.VALOR_PADRAO
                    logger.info(f"Campo 'TELEFONES' ausente. Valor padrão atribuído: {self.VALOR_PADRAO}")

            # Tratamento especial para EMAIL
            elif campo == "EMAIL":
                emails = dados.get("EMAIL", [])
                if emails and "EMAIL" in emails[0]:
                    dados_filtrados["EMAIL"] = self.tratar_valor(emails[0]["EMAIL"])
                    logger.debug(f"Campo 'EMAIL' tratado: {dados_filtrados['EMAIL']}")
                else:
                    dados_filtrados["EMAIL"] = self.VALOR_PADRAO
                    logger.debug(f"Campo 'EMAIL' ausente. Valor padrão atribuído: {self.VALOR_PADRAO}")

            # Campos genéricos
            elif campo in dados:
                dados_filtrados[campo] = self.tratar_valor(dados[campo])

            # Campo não presente nos dados
            else:
                dados_filtrados[campo] = self.VALOR_PADRAO
                logger.debug(f"Campo '{campo}' ausente. Valor padrão atribuído: {self.VALOR_PADRAO}")

        total_campos = len(campos_desejados)
        campos_filtrados = len([c for c in campos_desejados if c in dados_filtrados])
        campos_pulados = total_campos - campos_filtrados
        logger.info(
            f"Filtragem dos dados concluída. Campos filtrados: {campos_filtrados}, Campos pulados: {campos_pulados}."
        )
        return dados_filtrados