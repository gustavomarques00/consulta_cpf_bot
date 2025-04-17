import random
import logging
from utils.emoji import EMOJI

# Configuração do Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleSheetsService:
    def __init__(self, config, gspread, ServiceAccountCredentials):
        self.config = config
        self.gspread = gspread
        self.ServiceAccountCredentials = ServiceAccountCredentials

    def autenticar_google_sheets(self):
        """
        Autentica no Google Sheets usando as credenciais fornecidas.
        """
        try:
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
            ]
            creds = self.ServiceAccountCredentials.from_json_keyfile_name(
                self.config.CREDENTIALS_FILE, scope
            )
            return self.gspread.authorize(creds)
        except Exception as e:
            logger.error(f"{EMOJI['error']} Erro ao autenticar no Google Sheets: {e}")
            return None

    def obter_cpfs_da_aba_checker(self, sheet_checker):
        """
        Obtém todos os CPFs da aba 'Checker'.
        """
        try:
            linhas = sheet_checker.get_all_values()
            if len(linhas) <= 1:
                return []
            return [linha[0] for linha in linhas[1:]]
        except Exception as e:
            logger.error(f"{EMOJI['error']} Erro ao obter CPFs: {e}")
            return []

    def remover_linha_checker(self, sheet_checker, cpf):
        """
        Remove uma linha da aba 'Checker' com base no CPF fornecido.
        """
        try:
            linhas = sheet_checker.get_all_values()
            for idx, linha in enumerate(linhas[1:], start=2):
                if linha[0] == cpf:
                    sheet_checker.delete_rows(idx)
                    logger.info(
                        f"{EMOJI['remove']} CPF {cpf} removido da aba 'Checker'."
                    )
                    return
            logger.warning(
                f"{EMOJI['warn']} CPF {cpf} não encontrado na aba 'Checker'."
            )
        except Exception as e:
            logger.error(f"{EMOJI['error']} Erro ao remover CPF {cpf}: {e}")

    def reagendar_cpf_checker(self, sheet_checker, cpf):
        """
        Reagenda um CPF na aba 'Checker' para uma posição aleatória.
        """
        try:
            linhas = sheet_checker.get_all_values()
            posicao = random.randint(2, max(len(linhas), 2))
            sheet_checker.insert_row([cpf], posicao)
            logger.info(f"{EMOJI['loop']} CPF {cpf} reagendado para posição {posicao}.")
        except Exception as e:
            logger.error(f"{EMOJI['error']} Erro ao reagendar CPF {cpf}: {e}")
