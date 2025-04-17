from services.extracao_service import ExtracaoService
from core.config import Config

extracao_service = ExtracaoService(Config)

def test_filtrar_dados_api_success():
    """
    Testa a filtragem de dados retornados pela API com sucesso.
    """

    dados = {
        "NOME": "JOAO MARIA DE JESUS SKEZOSKI",
        "CPF": "03042528910",
        "SEXO": "M",
        "NASCIMENTO": "09/02/1978",
        "RENDA": "2578,86",
        "PODER_AQUISITIVO": "MEDIO",
        "TELEFONES": [
            {"NUMBER": "83988084707"},  # Celular válido
            {"NUMBER": "8332645551"},  # Não é celular
        ],
        "EMAIL": [{"EMAIL": "joao.silva@email.com"}],
    }
    campos_desejados = ["NOME", "SEXO", "RENDA", "TELEFONES", "EMAIL"]

    resultado = extracao_service.filtrar_dados_api(dados, campos_desejados)

    assert resultado["NOME"] == "JOAO MARIA DE JESUS SKEZOSKI"
    assert resultado["SEXO"] == "M"
    assert resultado["RENDA"] == "2578,86"
    assert resultado["TELEFONES"] == "83988084707"  # Primeiro celular válido
    assert resultado["EMAIL"] == "joao.silva@email.com"


def test_filtrar_dados_api_missing_fields():
    """
    Testa a filtragem de dados com campos ausentes.
    """
    extracao_service = ExtracaoService(Config)

    dados = {
        "NOME": "JOÃO MARIA DE JESUS SKEZOSKI",
        "CPF": "03042528910",
    }
    campos_desejados = ["NOME", "SEXO", "RENDA", "TELEFONES", "EMAIL"]

    resultado = extracao_service.filtrar_dados_api(dados, campos_desejados)

    assert resultado["NOME"] == "JOÃO MARIA DE JESUS SKEZOSKI"
    assert resultado["SEXO"] == "Não Informado"
    assert resultado["RENDA"] == "Não Informado"
    assert resultado["TELEFONES"] == "Não Informado"
    assert resultado["EMAIL"] == "Não Informado"
