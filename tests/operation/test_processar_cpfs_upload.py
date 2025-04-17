import pytest
from unittest.mock import patch


def test_processar_cpfs_upload_success(
    mock_operation_service, mock_consultar_api, mock_filtrar_dados_api
):
    """
    Testa o processamento de CPFs com sucesso.
    """
    # Dados de entrada
    cpfs = ["48489517045", "98765432100"]
    campos_desejados = ["NOME", "SEXO", "RENDA"]
    status_inicial = "Criar"

    # Configuração dos mocks
    mock_operation_service.processar_cpfs_upload.side_effect = lambda **kwargs: [
        {
            "cpf": cpf,
            "status": status_inicial,
            **mock_filtrar_dados_api(mock_consultar_api(cpf, None), campos_desejados),
        }
        for cpf in cpfs
    ]

    # Execução
    resultados = mock_operation_service.processar_cpfs_upload(
        chefe_id=1,
        cpfs=cpfs,
        campos_desejados=campos_desejados,
        status_inicial=status_inicial,
    )

    # Verificações
    assert (
        len(resultados) == 2
    ), "O número de resultados deve ser igual ao número de CPFs fornecidos."
    assert resultados[0] == {
        "cpf": "48489517045",
        "status": "Criar",
        "NOME": "João Silva",
        "SEXO": "M",
        "RENDA": "3000",
    }, "O primeiro resultado não corresponde ao esperado."
    assert resultados[1] == {
        "cpf": "98765432100",
        "status": "Criar",
        "NOME": "Maria Souza",
        "SEXO": "F",
        "RENDA": "4000",
    }, "O segundo resultado não corresponde ao esperado."


def test_processar_cpfs_upload_invalid_cpf(mock_operation_service):
    """
    Testa o processamento de CPFs com um CPF inválido.
    """
    # Dados de entrada
    cpfs = ["123"]
    campos_desejados = ["NOME", "SEXO", "RENDA"]
    status_inicial = "Criar"

    # Configuração do mock para simular o comportamento esperado
    mock_operation_service.processar_cpfs_upload.return_value = [
        {"cpf": "123", "status": "Formato Inválido"}
    ]

    # Execução
    resultados = mock_operation_service.processar_cpfs_upload(
        chefe_id=1,
        cpfs=cpfs,
        campos_desejados=campos_desejados,
        status_inicial=status_inicial,
    )

    # Verificações
    assert (
        len(resultados) == 1
    ), "O número de resultados deve ser 1 para um CPF inválido."
    assert resultados[0] == {
        "cpf": "123",
        "status": "Formato Inválido",
    }, "O resultado para o CPF inválido não corresponde ao esperado."
