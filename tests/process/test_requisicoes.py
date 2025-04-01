import time
from unittest.mock import patch, MagicMock
from utils.request_tracker import verificar_requisicoes_diarias
from backend.core.config import Config


def build_mocked_open(date_value: str, count_value: str):
    """
    Gera uma função mock para open(), simulando a leitura de:
    - request_date.txt -> date_value
    - request_count.txt -> count_value
    """

    def mocked_open(file, *args, **kwargs):
        mock_file = MagicMock()
        if str(file).endswith("request_date.txt"):
            mock_file.read.return_value = date_value
        elif str(file).endswith("request_count.txt"):
            mock_file.read.return_value = count_value
        else:
            raise FileNotFoundError(f"Arquivo não esperado: {file}")
        mock_file.__enter__.return_value = mock_file
        return mock_file

    return mocked_open


def test_verificar_requisicoes_diarias_limite_atingido():
    """
    Simula que:
    - request_date.txt contém a data de hoje
    - request_count.txt contém o número máximo de requisições (>= MAX_DAILY_REQUESTS)

    Esperado: verificar_requisicoes_diarias() deve retornar False
    """
    hoje = time.strftime("%Y-%m-%d")

    with patch("os.path.exists", return_value=True), patch(
        "builtins.open", new=build_mocked_open(hoje, str(Config.MAX_DAILY_REQUESTS))
    ):
        assert not verificar_requisicoes_diarias(Config)


def test_verificar_requisicoes_diarias_abaixo_limite():
    """
    Simula que:
    - request_date.txt contém a data de hoje
    - request_count.txt contém "3999" (abaixo do limite)

    Esperado: verificar_requisicoes_diarias() deve retornar True
    """
    hoje = time.strftime("%Y-%m-%d")

    with patch("os.path.exists", return_value=True), patch(
        "builtins.open", new=build_mocked_open(hoje, "3999")
    ):
        assert verificar_requisicoes_diarias(Config)
