import sys
import os
from utils.token import generate_tokens
from unittest import mock
import unittest
from scripts.ExtracaoAPI import verificar_requisicoes_diarias
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))
import pytest
from unittest.mock import patch

# =====================================
# Testes para verificação de requisições diárias
# =====================================

# Este teste verifica o comportamento da função 'verificar_requisicoes_diarias'
# em dois cenários distintos: quando o limite de requisições já foi atingido (4000)
# e quando ainda não foi (3999). A função deve retornar False no primeiro caso
# e True no segundo. O 'mock_open' simula a leitura do arquivo de contagem.
def test_verificar_requisicoes_diarias():
    # Simula o arquivo com 4000 requisições feitas
    with patch("builtins.open", unittest.mock.mock_open(read_data="4000")):
        assert not verificar_requisicoes_diarias()  # Espera que o retorno seja False

    # Simula o arquivo com 3999 requisições feitas
    with patch("builtins.open", unittest.mock.mock_open(read_data="3999")):
        assert verificar_requisicoes_diarias()  # Espera que o retorno seja True