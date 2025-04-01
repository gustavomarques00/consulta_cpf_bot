import sys
import os
import pytest
from unittest.mock import MagicMock
from utils.token import generate_tokens

# Adiciona o diretório 'scripts' ao sys.path, se necessário
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
)

# Importa as funções que serão testadas diretamente da pasta 'scripts'
from services.google_sheets_service import (
    remover_linha_checker,
    obter_cpfs_da_aba_checker,
)

# ---------------- FIXTURE COMUM ----------------


# Cria um mock para representar a aba "Checker" do Google Sheets
@pytest.fixture
def mock_sheet_checker():
    return MagicMock()


# ---------------- TESTE: remover_linha_checker ----------------


# Verifica se a função remove corretamente um CPF específico da aba 'Checker',
# que possui apenas uma coluna chamada "CPF". Cada CPF é removido após o processamento.
def test_remover_linha_checker(mock_sheet_checker):
    # Simula a aba 'Checker' com cabeçalho e dois CPFs
    mock_sheet_checker.get_all_values.return_value = [
        ["CPF"],  # Cabeçalho (coluna única)
        ["12345678901"],  # Linha 2 (deve ser removida)
        ["10987654321"],  # Linha 3
    ]

    # Executa a função para remover o CPF "12345678901"
    remover_linha_checker(mock_sheet_checker, "12345678901")

    # Verifica se a linha correta foi removida (linha 2)
    mock_sheet_checker.delete_rows.assert_called_once_with(2)


# ---------------- TESTE: obter_cpfs_da_aba_checker ----------------


# Verifica se a função retorna corretamente todos os CPFs da aba 'Checker'.
# Essa aba possui apenas a coluna "CPF" e é usada como fila para processamento.
def test_obter_cpfs_da_aba_checker(mock_sheet_checker):
    # Simula a aba 'Checker' com apenas uma coluna chamada "CPF"
    mock_sheet_checker.get_all_values.return_value = [
        ["CPF"],  # Cabeçalho
        ["12345678901"],  # Linha 2
        ["invalid_cpf"],  # Linha 3
        ["10987654321"],  # Linha 4
    ]

    # Executa a função que extrai os CPFs ignorando o cabeçalho
    cpfs = obter_cpfs_da_aba_checker(mock_sheet_checker)

    # Espera-se que retorne todas as linhas abaixo do cabeçalho (coluna A)
    assert cpfs == ["12345678901", "invalid_cpf", "10987654321"]
