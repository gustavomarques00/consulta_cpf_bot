import sys
import os
import pytest
from unittest.mock import MagicMock

# Adiciona o diretório 'scripts' ao sys.path, se necessário
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

from scripts.ExtracaoAPI import remover_linha_checker, obter_cpfs_da_aba_checker  # Importando corretamente da pasta 'scripts'

# Fixture para mockar a aba "Checker"
@pytest.fixture
def mock_sheet_checker():
    return MagicMock()

# Testa a remoção de um CPF na aba "Checker"
def test_remover_linha_checker(mock_sheet_checker):
    # Mock para retornar CPFs da aba
    mock_sheet_checker.get_all_values.return_value = [
        ["CPF", "Status"],
        ["12345678901", "Pendentes"],
        ["10987654321", "Pendentes"]
    ]
    
    # Chama a função para remover o CPF
    remover_linha_checker(mock_sheet_checker, "12345678901")

    # Verifica se a função delete_rows foi chamada com o índice correto
    mock_sheet_checker.delete_rows.assert_called_once_with(2)

# Testa a extração de CPFs válidos da aba "Checker"
def test_obter_cpfs_da_aba_checker(mock_sheet_checker):
    # Mock para retornar CPFs da aba
    mock_sheet_checker.get_all_values.return_value = [
        ["CPF", "Status"],
        ["12345678901", "Pendentes"],
        ["invalid_cpf", "Pendentes"],
        ["10987654321", "Pendentes"]
    ]
    
    # Chama a função para obter os CPFs
    cpfs = obter_cpfs_da_aba_checker(mock_sheet_checker)

    # Verifica se os CPFs retornados estão corretos
    assert cpfs == ["12345678901", "invalid_cpf", "10987654321"]
