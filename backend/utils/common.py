import re
import logging
from datetime import datetime

# Configuração de logs
logger = logging.getLogger(__name__)


def format_string_to_number(string: str) -> str:
    """
    Remove todos os caracteres não numéricos de uma string.
    """
    return re.sub(r"\D", "", string)


def current_timestamp() -> str:
    """
    Retorna o timestamp atual no formato ISO 8601.
    """
    return datetime.now().isoformat()


def is_valid_cargo(cargo: str, valid_cargos: list) -> bool:
    """
    Verifica se o cargo fornecido é válido.
    """
    return cargo in valid_cargos
