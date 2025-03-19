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
    #CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE", "credenciais.json")
    CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE", os.path.join(os.getcwd(), "backend", "credenciais.json"))
    SHEET_NAME = os.getenv("SHEET_NAME", "Operação JUVO")
    WORKSHEET_DATA = os.getenv("WORKSHEET_DATA", "Dados")
    WORKSHEET_CHECKER = os.getenv("WORKSHEET_CHECKER", "Checker")

    # Configurações do MySQL
    DB_HOST = os.getenv("DB_HOST", "localhost") # Host do banco de dados
    DB_USER = os.getenv("DB_USER", "root") # Usuário do banco de dados
    DB_PASSWORD = os.getenv("DB_PASSWORD", "") # Senha do banco de dados
    DB_NAME = os.getenv("DB_NAME", "sua_aplicacao") # Nome do banco de dados

    # Configurações do Flask
    FLASK_HOST = os.getenv("FLASK_HOST", "localhost") # Host do servidor Flask
    FLASK_PORT = os.getenv("FLASK_PORT", 5000) # Porta do servidor Flask

    # Configurações do Redis
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost") # Host do servidor Redis
    REDIS_PORT = os.getenv("REDIS_PORT", 6379) # Porta do servidor Redis

    # configurações da API
    API_TOKEN = os.getenv("API_TOKEN", "sua_chave") # Token da API
    API_URL = os.getenv("API_URL", "https://hashirosearch.xyz/cpf.php") # URL da API

    # Configurações de delay
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", 5)) # Delay entre tentativas de consulta à API
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3)) # Número máximo de tentativas de consulta à API


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
