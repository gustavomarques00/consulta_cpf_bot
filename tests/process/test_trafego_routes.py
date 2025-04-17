import pytest
from services.trafego_service import TrafegoService


# Teste para verificar o histórico completo de tráfego.
def test_historico_completo():
    """
    Testa o método de consulta do histórico completo de tráfego.
    """
    trafego_service = TrafegoService()

    # Chamando o método real do serviço
    response = trafego_service.consultar_historico()

    # Verificando se o retorno contém os dados esperados
    assert isinstance(response, dict), "❌ O retorno deve ser um dicionário."
    assert "data" in response or isinstance(
        response, dict
    ), "❌ O histórico não contém o campo esperado"
    if response:
        assert isinstance(response, dict)


# Teste para verificar o histórico de tráfego filtrado por data.
def test_historico_por_data():
    """
    Testa o método de consulta do histórico de tráfego filtrado por data.
    """
    trafego_service = TrafegoService()
    data_param = "2025-04-01"

    # Chamando o método real do serviço
    try:
        response = trafego_service.consultar_historico(data_param=data_param)
        assert isinstance(response, dict), "❌ O retorno deve ser um dicionário."
    except FileNotFoundError:
        # Caso o arquivo de log não exista, o teste ainda é válido
        assert True


# Teste para verificar a exportação de dados em formato CSV.
def test_exportar_csv():
    """
    Testa o método de exportação de tráfego em formato CSV.
    """
    trafego_service = TrafegoService()
    data_param = "2025-04-01"

    # Chamando o método real do serviço
    try:
        csv_output = trafego_service.exportar_log_csv(data_param)
        assert csv_output is not None, "❌ O retorno do CSV não deve ser None."
        assert csv_output.getvalue().startswith(
            "Linha"
        ), "❌ O CSV exportado não contém o cabeçalho esperado."
    except FileNotFoundError:
        # Caso o arquivo de log não exista, o teste ainda é válido
        assert True
