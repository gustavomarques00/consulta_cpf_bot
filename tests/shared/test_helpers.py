import sys
import os
import pytest
from unittest.mock import MagicMock

# Garante que os módulos da pasta "scripts" sejam encontrados
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
)

# Importa as funções responsáveis por manipular a aba "Checker"
from services.google_sheets_service import (
    remover_linha_checker,
    obter_cpfs_da_aba_checker,
)

# =============================
# FIXTURE: MOCK DO GOOGLE SHEETS
# =============================


@pytest.fixture
def mock_sheet_checker():
    """
    Retorna um mock que simula a aba 'Checker' do Google Sheets,
    usada para armazenar a fila de CPFs a serem processados.
    """
    return MagicMock()


# =============================
# TESTE: REMOVER CPF DA ABA CHECKER
# =============================


def test_remover_linha_checker(mock_sheet_checker):
    """
    Testa se a função remove corretamente o CPF da aba 'Checker'.

    Simula a planilha com duas linhas de CPF após o cabeçalho.
    Verifica se a função detecta corretamente o CPF alvo e chama delete_rows com a linha correspondente.
    """
    mock_sheet_checker.get_all_values.return_value = [
        ["CPF"],  # Cabeçalho (linha 1)
        ["12345678901"],  # Linha 2 (deve ser removida)
        ["10987654321"],  # Linha 3
    ]

    # Chama a função para remover o CPF "12345678901"
    remover_linha_checker(mock_sheet_checker, "12345678901")

    # A linha 2 deve ser removida (índice 2 no Google Sheets)
    mock_sheet_checker.delete_rows.assert_called_once_with(2)


# =============================
# TESTE: OBTER TODOS OS CPFs DA ABA CHECKER
# =============================


def test_obter_cpfs_da_aba_checker(mock_sheet_checker):
    """
    Testa se a função extrai corretamente os CPFs da aba 'Checker'.

    Simula a planilha com 3 CPFs, ignorando o cabeçalho.
    Verifica se os valores extraídos correspondem à coluna única da planilha.
    """
    mock_sheet_checker.get_all_values.return_value = [
        ["CPF"],  # Cabeçalho
        ["12345678901"],  # Linha 2
        ["99988877766"],  # Linha 3
        ["45612378900"],  # Linha 4
    ]

    cpfs = obter_cpfs_da_aba_checker(mock_sheet_checker)

    # Deve retornar apenas os CPFs como strings, sem o cabeçalho
    assert cpfs == ["12345678901", "99988877766", "45612378900"]
