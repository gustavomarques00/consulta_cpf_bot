import sys
import os
import unittest
from unittest.mock import patch
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))
from unittest.mock import MagicMock
from scripts.ExtracaoAPI import processar_lote_cpfs, processar_cpf, consultar_api  # Importando corretamente da pasta 'scripts'

@pytest.fixture
def mock_sheet_data():
    return MagicMock()

@pytest.fixture
def mock_sheet_checker():
    return MagicMock()

# Testa o processamento de CPFs em lotes
def test_processar_lote_cpfs(mock_sheet_data, mock_sheet_checker):
    cpfs = ["12345678901", "10987654321", "11223344556", "22334455667"]
    batch_size = 2

    # Mock da função processar_cpf
    with patch("scripts.ExtracaoAPI.processar_cpf") as mock_processar_cpf:
        processar_lote_cpfs(cpfs, mock_sheet_data, mock_sheet_checker, batch_size)

    # Verifica se processar_cpf foi chamado corretamente
    assert mock_processar_cpf.call_count == 2  # Deveria chamar 2 vezes por lote
    mock_processar_cpf.assert_any_call("12345678901", mock_sheet_data, mock_sheet_checker)
    mock_processar_cpf.assert_any_call("10987654321", mock_sheet_data, mock_sheet_checker)

# Testa o processamento de um único CPF
def test_processar_cpf(mock_sheet_data, mock_sheet_checker):
    cpf = "12345678901"
    
    # Mock da função consultar_api
    with patch("scripts.ExtracaoAPI.consultar_api", return_value={"NOME": "Gustavo"}) as mock_consultar_api:
        processar_cpf(cpf, mock_sheet_data, mock_sheet_checker)

    # Verifica se o CPF foi processado
    mock_consultar_api.assert_called_once_with(cpf)
    mock_sheet_data.append_row.assert_called_once()
    # Verifica se o CPF foi adicionado à planilha