import io
import pytest
from services.extracao_service import ExtracaoService
from core.config import Config
from unittest.mock import patch
import logging

# instância do serviço de extração para obter os campos permitidos
extracao_service = ExtracaoService(Config)

# Configura o logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def test_upload_cpfs_invalid_file(client, chefe_token):
    """
    Testa o upload de CPFs com um arquivo inválido.
    """
    response = client.post(
        "/operacaoes/upload-cpfs",
        data={"file": (None, ""), "campos": "NOME,CPF"},
        content_type="multipart/form-data",
        headers={"Authorization": f"Bearer {chefe_token}"},
    )

    assert (
        response.status_code == 400
    ), "O status code deve ser 400 para arquivo inválido."
    data = response.get_json()
    assert data is not None, "A resposta deve conter dados JSON."
    assert "error" in data, "A resposta deve conter a chave 'error'."
    assert (
        data["error"] == "O nome do arquivo está vazio."
    ), "A mensagem de erro está incorreta."


def test_upload_cpfs_success(client, mock_csv_file, chefe_token):
    """
    Testa o upload de CPFs com sucesso, utilizando os campos permitidos
    definidos no serviço de extração e simulando um processamento bem-sucedido.
    """
    logger.info("Iniciando o teste de upload de CPFs com sucesso.")

    # Converte o mock_csv_file (StringIO) para BytesIO
    file_bytes = io.BytesIO(mock_csv_file.getvalue().encode("utf-8"))
    logger.debug("Arquivo mock convertido para BytesIO.")

    # Reinstancia o serviço para obter os campos permitidos
    extracao_service = ExtracaoService(Config)

    # Certifique-se de que CAMPOS_PERMITIDOS está configurado corretamente
    campos_validos = extracao_service.CAMPOS_PERMITIDOS
    if (
        not campos_validos
    ):  # Caso CAMPOS_PERMITIDOS esteja vazio, forneça valores padrão
        logger.warning("CAMPOS_PERMITIDOS está vazio. Usando valores padrão.")
        campos_validos = ["NOME", "CPF", "SEXO", "NASCIMENTO"]

    logger.debug(f"Campos permitidos utilizados: {campos_validos}")

    # Patch do método processar_cpfs_upload para simular sucesso
    with patch(
        "backend.services.operation_service.OperationService.processar_cpfs_upload",
        return_value=[
            {"cpf": "48489517045", "status": "Formato Inválido"},
            {"cpf": "98765432100", "status": "Nenhum dado encontrado"},
        ],
    ):
        logger.info("Simulando o processamento de upload de CPFs.")
        response = client.post(
            "/operacaoes/upload-cpfs",
            data={
                "file": (file_bytes, "cpfs.csv"),
                "campos": ",".join(
                    campos_validos
                ),  # Envia campos válidos como string separada por vírgulas
                "status_inicial": "Criar",
            },
            content_type="multipart/form-data",
            headers={"Authorization": f"Bearer {chefe_token}"},
        )

    # Verificações
    logger.debug("Verificando a resposta do upload.")
    assert (
        response.status_code == 200
    ), "O status code deve ser 200 para upload bem-sucedido."
    data = response.get_json()
    assert data is not None, "A resposta deve conter dados JSON."
    assert "message" in data, "A resposta deve conter a chave 'message'."
    assert (
        data["message"] == "Arquivo processado com sucesso."
    ), "A mensagem de sucesso está incorreta."
    assert "resultados" in data, "A resposta deve conter a chave 'resultados'."
    assert len(data["resultados"]) == 2, "A resposta deve conter dois resultados."
    assert (
        data["resultados"][0]["cpf"] == "48489517045"
    ), "O CPF do primeiro resultado está incorreto."
    assert (
        data["resultados"][1]["cpf"] == "98765432100"
    ), "O CPF do segundo resultado está incorreto."

    logger.info("Teste de upload de CPFs com sucesso concluído.")


def test_upload_cpfs_missing_fields(client, mock_csv_file, chefe_token):
    """
    Testa o upload de CPFs com campos ausentes no payload.
    """
    logger.info("Iniciando o teste de upload de CPFs com campos ausentes.")

    # Converte o mock_csv_file (StringIO) para BytesIO
    file_bytes = io.BytesIO(mock_csv_file.getvalue().encode("utf-8"))
    logger.debug("Arquivo mock convertido para BytesIO.")

    response = client.post(
        "/operacaoes/upload-cpfs",
        data={"file": (file_bytes, "cpfs.csv")},  # Campos ausentes
        query_string={"campos": "INVALIDO"},  # Envia um campo inválido
        content_type="multipart/form-data",
        headers={"Authorization": f"Bearer {chefe_token}"},
    )

    # Verificações
    logger.debug("Verificando a resposta do upload com campos ausentes.")
    assert (
        response.status_code == 400
    ), "O status code deve ser 400 para campos ausentes."
    data = response.get_json()
    assert data is not None, "A resposta deve conter dados JSON."
    assert "error" in data, "A resposta deve conter a chave 'error'."
    assert data["error"] == "Campos inválidos", "A mensagem de erro está incorreta."

    logger.info("Teste de upload de CPFs com campos ausentes concluído.")


def test_upload_cpfs_unauthorized(client, mock_csv_file):
    """
    Testa o upload de CPFs sem autorização (token ausente).
    """
    logger.info("Iniciando o teste de upload de CPFs sem autorização.")

    # Converte o mock_csv_file (StringIO) para BytesIO
    file_bytes = io.BytesIO(mock_csv_file.getvalue().encode("utf-8"))
    logger.debug("Arquivo mock convertido para BytesIO.")

    response = client.post(
        "/operacaoes/upload-cpfs",
        data={"file": (file_bytes, "cpfs.csv"), "campos": "NOME,CPF"},
        content_type="multipart/form-data",
    )  # Sem o cabeçalho de autorização

    # Verificações
    logger.debug("Verificando a resposta do upload sem autorização.")
    assert (
        response.status_code == 401
    ), "O status code deve ser 401 para requisição não autorizada."
    data = response.get_json()
    assert data is not None, "A resposta deve conter dados JSON."
    assert "error" in data, "A resposta deve conter a chave 'error'."
    assert (
        data["error"] == "Token não fornecido ou malformado!"
    ), "A mensagem de erro está incorreta."

    logger.info("Teste de upload de CPFs sem autorização concluído.")


def test_upload_cpfs_invalid_token(client, mock_csv_file):
    """
    Testa o upload de CPFs com um token inválido.
    """
    logger.info("Iniciando o teste de upload de CPFs com token inválido.")

    # Converte o mock_csv_file (StringIO) para BytesIO
    file_bytes = io.BytesIO(mock_csv_file.getvalue().encode("utf-8"))
    logger.debug("Arquivo mock convertido para BytesIO.")

    response = client.post(
        "/operacaoes/upload-cpfs",
        data={"file": (file_bytes, "cpfs.csv"), "campos": "NOME,CPF"},
        content_type="multipart/form-data",
        headers={"Authorization": "Bearer invalid_token"},
    )

    # Verificações
    logger.debug("Verificando a resposta do upload com token inválido.")
    assert (
        response.status_code == 401
    ), "O status code deve ser 401 para token inválido."
    data = response.get_json()
    assert data is not None, "A resposta deve conter dados JSON."
    assert "error" in data, "A resposta deve conter a chave 'error'."
    assert data["error"] == "Token inválido!", "A mensagem de erro está incorreta."

    logger.info("Teste de upload de CPFs com token inválido concluído.")


def test_upload_cpfs_large_file(client, chefe_token):
    """
    Testa o upload de CPFs com um arquivo muito grande.
    """
    logger.info("Iniciando o teste de upload de CPFs com arquivo grande.")

    # Gera um arquivo grande
    large_file_content = "NOME,CPF\n" + "\n".join(
        [f"Nome{i},1234567890{i}" for i in range(100000)]
    )
    file_bytes = io.BytesIO(large_file_content.encode("utf-8"))
    logger.debug("Arquivo grande gerado e convertido para BytesIO.")

    response = client.post(
        "/operacaoes/upload-cpfs",
        data={"file": (file_bytes, "large_cpfs.csv"), "campos": "NOME,CPF"},
        content_type="multipart/form-data",
        headers={"Authorization": f"Bearer {chefe_token}"},
    )

    # Verificações
    logger.debug("Verificando a resposta do upload com arquivo grande.")
    assert response.status_code in [
        200,
        413,
    ], "O status code deve ser 200 ou 413 para arquivo grande."
    if response.status_code == 413:
        data = response.get_json()
        assert data is not None, "A resposta deve conter dados JSON."
        assert "error" in data, "A resposta deve conter a chave 'error'."
        assert (
            data["error"] == "O arquivo enviado é muito grande."
        ), "A mensagem de erro está incorreta."

    logger.info("Teste de upload de CPFs com arquivo grande concluído.")
