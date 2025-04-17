import os
from unittest.mock import MagicMock
from dotenv import load_dotenv
import pytest
from io import StringIO

# Importações de módulos do projeto
from core.config import Config
from core.db import get_db_connection
from services.google_sheets_service import GoogleSheetsService
from services.token_service import TokenService
from services.operation_service import OperationService
from services.notification_service import NotificationService
from backend.services.extracao_service import ExtracaoService
from main import app

# 🔄 Carrega as variáveis do .env para uso nos testes
load_dotenv()

# 🌍 Configurações globais
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")
JWT_SECRET = os.getenv("JWT_SECRET", "defaultsecret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
real_token_service = TokenService(jwt_secret=JWT_SECRET, jwt_algorithm=JWT_ALGORITHM)

# ================================
# FIXTURES PARA O TESTE
# ================================


@pytest.fixture(scope="module")
def base_url() -> str:
    """Retorna a URL base para os testes."""
    return BASE_URL


@pytest.fixture(scope="module")
def headers() -> dict:
    """Cabeçalhos padrão para testes de API (Content-Type JSON)."""
    return {"Content-Type": "application/json"}


@pytest.fixture(scope="module")
def token():
    """
    Gera um token de acesso válido usando o TokenService.
    """
    user_id = 1  # ID do usuário de teste
    cargo = "ADM"  # Cargo do usuário de teste
    return real_token_service.generate_access_token(user_id, cargo)


@pytest.fixture(scope="module")
def invalid_token():
    """
    Gera um token inválido para testes.
    """
    valid_token = real_token_service.generate_access_token(1, "ADM")
    return valid_token[:10] + "invalid_part"  # Corrompe o token


@pytest.fixture(scope="module")
def refresh_token():
    """
    Gera um refresh_token válido usando o TokenService.
    """
    user_id = 1  # ID do usuário de teste
    return real_token_service.generate_refresh_token(user_id)


@pytest.fixture(scope="module")
def chefe_token():
    """
    Gera um token de acesso válido para o Chefe de Equipe.
    """
    user_id = 1  # ID do Chefe de Equipe
    cargo = "CHEFE DE EQUIPE"
    return real_token_service.generate_access_token(user_id, cargo)


@pytest.fixture(scope="module")
def operador_token():
    """
    Gera um token de acesso válido para o Operador.
    """
    user_id = 7  # ID do Operador
    cargo = "OPERADOR"
    return real_token_service.generate_access_token(user_id, cargo)


# ================================
# MOCKS PARA SERVIÇOS
# ================================


@pytest.fixture
def mock_operation_service():
    """
    Mock do serviço OperationService.
    """
    return MagicMock(spec=OperationService)


@pytest.fixture
def mock_notification_service():
    """
    Mock do serviço NotificationService.
    """
    return MagicMock(spec=NotificationService)


@pytest.fixture
def mock_filtrar_dados_api():
    """
    Mock da função filtrar_dados_api.
    """

    def mock_func(dados, campos_desejados):
        return {campo: dados.get(campo, "Não Informado") for campo in campos_desejados}

    return mock_func


@pytest.fixture
def mock_consultar_api(monkeypatch):
    """
    Substitui o método ExtracaoService.consultar_api para
    retornar dados pré-definidos para CPFs de teste.
    """
    def _mock_consultar_api(cpf, sheet_checker=None, reagendar_func=None):
        if cpf == "48489517045":
            return {"NOME": "João Silva", "SEXO": "M", "RENDA": "3000"}
        elif cpf == "98765432100":
            return {"NOME": "Maria Souza", "SEXO": "F", "RENDA": "4000"}
        # Para qualquer outro CPF, retorna dict vazio
        return {}
    monkeypatch.setattr(ExtracaoService, "consultar_api", _mock_consultar_api)
    return _mock_consultar_api

@pytest.fixture
def mock_csv_file():
    """
    Mock de um arquivo CSV contendo CPFs.
    """
    csv_content = "cpf\n48489517045\n98765432100\n"
    return StringIO(csv_content)


@pytest.fixture
def client():
    """
    Configura um cliente de teste para a aplicação Flask.
    """
    app.config["TESTING"] = True  # Ativa o modo de teste
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_google_sheets_service():
    """
    Mock da classe GoogleSheetsService.
    """
    return GoogleSheetsService(Config, MagicMock(), MagicMock())


@pytest.fixture
def mock_sheet_checker():
    """
    Mock para representar a aba 'Checker' do Google Sheets.
    """
    return MagicMock()


@pytest.fixture
def operation_service(mock_operation_service):
    return mock_operation_service


@pytest.fixture
def notification_service(mock_notification_service):
    return mock_notification_service


@pytest.fixture
def trafego_service(mock_trafego_service):
    return mock_trafego_service


@pytest.fixture
def mock_token_service():
    """
    Mock do serviço TokenService.
    """
    mock_service = MagicMock(spec=TokenService)
    mock_service.revogar_access_token = MagicMock()
    mock_service.is_token_blacklisted = MagicMock(return_value=True)
    return mock_service


@pytest.fixture
def verificar_erro_resposta():
    """
    Fixture que retorna uma função helper para verificar erros na resposta.
    """

    def helper(response):
        if "error" in response:
            pytest.fail(f"Erro ao enviar pedido: {response['error']}")

    return helper
