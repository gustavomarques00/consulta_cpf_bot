import pytest


def test_remover_linha_checker(mock_google_sheets_service, mock_sheet_checker):
    """
    Testa se a função remove corretamente um CPF específico da aba 'Checker'.
    """
    # Simula a aba 'Checker' com cabeçalho e dois CPFs
    mock_sheet_checker.get_all_values.return_value = [
        ["CPF"],  # Cabeçalho (coluna única)
        ["48489517045"],  # Linha 2 (deve ser removida)
        ["10987654321"],  # Linha 3
    ]

    # Executa o método para remover o CPF "48489517045"
    mock_google_sheets_service.remover_linha_checker(mock_sheet_checker, "48489517045")

    # Verifica se a linha correta foi removida (linha 2)
    mock_sheet_checker.delete_rows.assert_called_once_with(2)


def test_obter_cpfs_da_aba_checker(mock_google_sheets_service, mock_sheet_checker):
    """
    Testa se a função retorna corretamente todos os CPFs da aba 'Checker'.
    """
    # Simula a aba 'Checker' com apenas uma coluna chamada "CPF"
    mock_sheet_checker.get_all_values.return_value = [
        ["CPF"],  # Cabeçalho
        ["48489517045"],  # Linha 2
        ["invalid_cpf"],  # Linha 3
        ["10987654321"],  # Linha 4
    ]

    # Executa o método que extrai os CPFs ignorando o cabeçalho
    cpfs = mock_google_sheets_service.obter_cpfs_da_aba_checker(mock_sheet_checker)

    # Espera-se que retorne todas as linhas abaixo do cabeçalho (coluna A)
    assert cpfs == ["48489517045", "invalid_cpf", "10987654321"]
