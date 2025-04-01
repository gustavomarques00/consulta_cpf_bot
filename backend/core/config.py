import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from utils.emoji import EMOJI  # ✅ Emojis centralizados

# Carregar variáveis do arquivo .env
load_dotenv()


class Config:
    """Classe para armazenar configurações do sistema."""

    # Diretório base do projeto
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    # ===============================
    # 📂 Caminho para arquivos de controle de requisições
    # ===============================
    REQUEST_TRACKER_PATH = Path(
        os.getenv("REQUEST_TRACKER_PATH", os.path.join(BASE_DIR, "logs", "requests"))
    )

    # ===============================
    # 🤖 Telegram
    # ===============================
    API_ID = os.getenv("API_ID")
    API_HASH = os.getenv("API_HASH")
    PHONE_NUMBER = os.getenv("PHONE_NUMBER")
    BOT_USERNAME = os.getenv("BOT_USERNAME")
    TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")

    # ===============================
    # 📊 Google Sheets
    # ===============================
    DEFAULT_CREDENTIALS_PATH = os.path.join(
        BASE_DIR, "shared", "credentials", "credenciais.json"
    )
    CREDENTIALS_FILE_RAW = os.getenv("CREDENTIALS_FILE")
    CREDENTIALS_FILE = (
        CREDENTIALS_FILE_RAW
        if CREDENTIALS_FILE_RAW and os.path.exists(CREDENTIALS_FILE_RAW)
        else DEFAULT_CREDENTIALS_PATH
    )
    SHEET_NAME = os.getenv("SHEET_NAME", "Operação JUVO")
    WORKSHEET_DATA = os.getenv("WORKSHEET_DATA", "Dados")
    WORKSHEET_CHECKER = os.getenv("WORKSHEET_CHECKER", "Checker")
    SHEET_ID = os.getenv("SHEET_ID")

    # ===============================
    # 🛠️ Banco de Dados (MySQL)
    # ===============================
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "sua_aplicacao")

    # ===============================
    # 🌐 API de Consulta
    # ===============================
    API_TOKEN = os.getenv("API_TOKEN", "sua_chave")
    API_URL = os.getenv("API_URL", "https://datawolf.tech/api.php")

    # ===============================
    # 🔐 Autenticação JWT
    # ===============================
    JWT_SECRET = os.getenv("JWT_SECRET", "segredo_forte")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRES = int(os.getenv("JWT_EXPIRES", 7200))  # segundos

    # ===============================
    # ⚙️ Outros
    # ===============================
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", 5))
    RETRY_DELAY_LONG = int(os.getenv("RETRY_DELAY_LONG", 10))
    MAX_DAILY_REQUESTS = int(os.getenv("MAX_DAILY_REQUESTS", 4600))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))

    BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")
    DOWNLOAD_FOLDER = "downloads/"

    # ===============================
    # 🧪 Usuário de Teste
    # ===============================
    TEST_USER_ID = os.getenv("TEST_USER_ID")
    TEST_USER_CARGO = os.getenv("TEST_USER_CARGO")

    # ===============================
    # 🔐 Credenciais WolfBuscas (opcional)
    # ===============================
    WOLFBUSCAS_USERNAME = os.getenv("WOLFBUSCAS_USERNAME", "xakep")
    WOLFBUSCAS_PASSWORD = os.getenv("WOLFBUSCAS_PASSWORD", "SenhadoWolf2025@")

    # ===============================
    # ✅ Validação Inicial
    # ===============================
    @staticmethod
    def validar_config():
        """Verifica se todas as configurações obrigatórias estão definidas corretamente."""

        required_fields = [
            ("API_ID", Config.API_ID),
            ("API_HASH", Config.API_HASH),
            ("PHONE_NUMBER", Config.PHONE_NUMBER),
            ("BOT_USERNAME", Config.BOT_USERNAME),
            ("CREDENTIALS_FILE", Config.CREDENTIALS_FILE),
        ]

        print(
            f"{EMOJI['info']} Caminho absoluto esperado: {os.path.abspath(Config.CREDENTIALS_FILE)}"
        )

        for field, value in required_fields:
            if not value:
                raise ValueError(
                    f"{EMOJI['error']} ERRO: A variável {field} não está definida corretamente no .env!"
                )

        if not os.path.exists(Config.CREDENTIALS_FILE):
            print(
                f"{EMOJI['warn']} O caminho do arquivo de credenciais parece incorreto."
            )
            print(
                f"{EMOJI['info']} Dica: verifique se sua variável CREDENTIALS_FILE no .env está assim:"
            )
            print("    CREDENTIALS_FILE=shared/credentials/credenciais.json")
            print(
                f"{EMOJI['info']} Caminho atual configurado: {Config.CREDENTIALS_FILE}"
            )
            print(
                f"{EMOJI['info']} Caminho absoluto resolvido: {os.path.abspath(Config.CREDENTIALS_FILE)}"
            )
            raise FileNotFoundError(
                f"{EMOJI['error']} O arquivo {Config.CREDENTIALS_FILE} não foi encontrado! Verifique as credenciais do Google Sheets."
            )

        # Garante que a pasta de downloads exista
        os.makedirs(Config.DOWNLOAD_FOLDER, exist_ok=True)


# ✅ Validação automática ao importar
Config.validar_config()
