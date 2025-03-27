import sys
import os
import requests
from unittest.mock import patch

# Adiciona o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.ExtracaoAPI import consultar_api  # Importando corretamente da pasta 'scripts'

# Testa o comportamento de consulta à API
def test_consultar_api_sucesso():
    cpf = "12345678901"
    mock_response = {
        "NOME": "Gustavo",
        "CPF": cpf,
        "SEXO": "M",
        "RENDA": "5000",
        "PODER_AQUISITIVO": "Alto",
        "EMAIL": [{"EMAIL": "gustavo@email.com"}],
        "TELEFONES": [{"NUMBER": "11912345678"}]
    }

    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response
        result = consultar_api(cpf)
    
    assert result is not None
    assert result["NOME"] == "Gustavo"
    assert result["CPF"] == cpf

# Testa o erro ao consultar a API
def test_consultar_api_erro():
    cpf = "12345678901"
    
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Erro na API")
        result = consultar_api(cpf)
    
    assert result is None