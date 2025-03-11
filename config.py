import os
import dotenv

# Carregar variáveis do arquivo .env
dotenv.load_dotenv()

class Config:
    """Classe para armazenar configurações do bot."""
    
    # Configurações do Telegram
    API_ID = os.getenv("API_ID")
    API_HASH = os.getenv("API_HASH")
    PHONE_NUMBER = os.getenv("PHONE_NUMBER")
    BOT_USERNAME = os.getenv("BOT_USERNAME")

    # Configurações do Google Sheets
    CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE", "credenciais.json")
    SHEET_NAME = os.getenv("SHEET_NAME", "Operação JUVO")
    WORKSHEET_DATA = os.getenv("WORKSHEET_DATA", "Dados")
    WORKSHEET_CHECKER = os.getenv("WORKSHEET_CHECKER", "Checker")

    # Diretório de downloads
    DOWNLOAD_FOLDER = "downloads/"
    
    # Validação inicial
    @staticmethod
    def validar_config():
        """Verifica se todas as configurações obrigatórias estão definidas corretamente."""
        required_fields = [
            ("API_ID", Config.API_ID),
            ("API_HASH", Config.API_HASH),
            ("PHONE_NUMBER", Config.PHONE_NUMBER),
            ("BOT_USERNAME", Config.BOT_USERNAME),
            ("CREDENTIALS_FILE", Config.CREDENTIALS_FILE)
        ]
        
        for field, value in required_fields:
            if not value:
                raise ValueError(f"❌ ERRO: A variável {field} não está definida corretamente no .env!")

        if not os.path.exists(Config.CREDENTIALS_FILE):
            raise FileNotFoundError(f"❌ O arquivo {Config.CREDENTIALS_FILE} não foi encontrado! Verifique as credenciais do Google Sheets.")

        # Criar a pasta de downloads, se não existir
        if not os.path.exists(Config.DOWNLOAD_FOLDER):
            os.makedirs(Config.DOWNLOAD_FOLDER)

# Validar configurações ao importar o módulo
Config.validar_config()
