import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))
import pytest
from unittest.mock import patch

# Testa o limite de requisições diárias
def test_verificar_requisicoes_diarias():
    # Simula o arquivo com 4000 requisições feitas
    with patch("builtins.open", unittest.mock.mock_open(read_data="4000")):
        assert not verificar_requisicoes_diarias()  # Espera que o retorno seja False

    # Simula o arquivo com 3999 requisições feitas
    with patch("builtins.open", unittest.mock.mock_open(read_data="3999")):
        assert verificar_requisicoes_diarias()  # Espera que o retorno seja True
