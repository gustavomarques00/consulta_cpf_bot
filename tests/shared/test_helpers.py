import pytest
import requests
from utils.validators import is_valid_email, validar_formato_cpf
from services.google_sheets_service import (
    remover_linha_checker,
    obter_cpfs_da_aba_checker,
)
from tests.conftest import BASE_URL  # Importa diretamente do conftest.py

# ================================
# TESTES DE FUNÇÕES E INTEGRAÇÃO
# ================================


def test_remover_linha_checker(mock_sheet_checker):
    """
    Testa a funcionalidade de remover uma linha específica da aba 'Checker' no Google Sheets.
    Simula a planilha com duas linhas de CPF após o cabeçalho.
    Verifica se a função detecta corretamente o CPF alvo e chama delete_rows com a linha correspondente.
    """
    # Simula os valores da planilha, incluindo cabeçalho e duas linhas de CPFs
    mock_sheet_checker.get_all_values.return_value = [
        ["CPF"],  # Cabeçalho (linha 1)
        ["12345678901"],  # Linha 2 (deve ser removida)
        ["10987654321"],  # Linha 3
    ]

    # Chama a função para remover o CPF "12345678901"
    remover_linha_checker(mock_sheet_checker, "12345678901")

    # Verifica se a função delete_rows foi chamada com o índice correto (linha 2)
    mock_sheet_checker.delete_rows.assert_called_once_with(2)


def test_obter_cpfs_da_aba_checker(mock_sheet_checker):
    """
    Testa a funcionalidade de obter todos os CPFs da aba 'Checker' no Google Sheets.
    Simula a planilha com 3 CPFs, ignorando o cabeçalho.
    Verifica se os valores extraídos correspondem à coluna única da planilha.
    """
    # Simula os valores da planilha, incluindo cabeçalho e três linhas de CPFs
    mock_sheet_checker.get_all_values.return_value = [
        ["CPF"],  # Cabeçalho
        ["12345678901"],  # Linha 2
        ["99988877766"],  # Linha 3
        ["45612378900"],  # Linha 4
    ]

    # Chama a função para obter os CPFs
    cpfs = obter_cpfs_da_aba_checker(mock_sheet_checker)

    # Verifica se os CPFs retornados estão corretos (sem o cabeçalho)
    assert cpfs == ["12345678901", "99988877766", "45612378900"]


def test_validar_cpf_formatado():
    """
    Testa a funcionalidade de validação de formato de CPF.
    Verifica se um CPF válido retorna True e um inválido retorna False.
    """
    valid_cpf = "123.456.789-09"  # CPF válido
    invalid_cpf = "123.456.789-00"  # CPF inválido (dígitos verificadores inválidos)

    # Verifica se a função retorna True para o CPF válido e False para o inválido
    assert validar_formato_cpf(valid_cpf) is True
    assert validar_formato_cpf(invalid_cpf) is False


def test_validar_email():
    """
    Testa a funcionalidade de validação de formato de email.
    Verifica se um email válido retorna True e um inválido retorna False.
    """
    valid_email = "test@example.com"
    invalid_email = "test@com"

    # Verifica se a função retorna True para o email válido e False para o inválido
    assert is_valid_email(valid_email) is True
    assert is_valid_email(invalid_email) is False
