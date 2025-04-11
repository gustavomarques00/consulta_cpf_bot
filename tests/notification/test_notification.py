import pytest
import requests
from tests.conftest import BASE_URL
from venv import logger


def test_notificar_operador_erro_interno(chefe_token, headers):
    """
    Testa o envio de notificação para um operador quando ocorre um erro interno no servidor.
    """
    payload = {
        "operador_id": 7,  # ID do operador válido
        "mensagem": "Teste de erro interno.",  # Mensagem que aciona o erro interno
    }

    response = requests.post(
        f"{BASE_URL}/notificacoes/notificar-operador",
        json=payload,
        headers={**headers, "Authorization": f"Bearer {chefe_token}"},
    )

    # Verifica se o código de status é 500
    assert response.status_code == 500, f"Esperado erro 500, mas obteve {response.status_code}. Resposta: {response.text}"

    # Verifica se a mensagem de erro está presente na resposta
    data = response.json()
    assert "error" in data, "Resposta não contém a chave 'error'"
    assert "Erro interno simulado para teste." in data["error"], "Mensagem de erro inesperada"


def test_notificar_operador_sem_autorizacao(headers):
    """
    Testa o envio de notificação sem fornecer o token de autorização.
    """
    payload = {
        "operador_id": 7,  # ID do operador válido
        "mensagem": "Você recebeu novos dados para processar.",
    }

    response = requests.post(
        f"{BASE_URL}/notificacoes/notificar-operador",
        json=payload,
        headers=headers,  # Sem o token de autorização
    )

    assert response.status_code == 401, f"Esperado erro 401, mas obteve {response.status_code}. Resposta: {response.text}"
    data = response.json()
    assert data["error"] == "Token não fornecido", "Mensagem de erro inesperada"


def test_notificar_operador_payload_invalido(chefe_token, headers):
    """
    Testa o envio de notificação com um payload inválido.
    """
    payload = {
        "operador_id": "invalid_id",  # ID inválido
        "mensagem": 12345,  # Mensagem inválida
    }

    response = requests.post(
        f"{BASE_URL}/notificacoes/notificar-operador",
        json=payload,
        headers={**headers, "Authorization": f"Bearer {chefe_token}"},
    )

    assert response.status_code == 400, f"Esperado erro 400, mas obteve {response.status_code}. Resposta: {response.text}"
    data = response.json()
    assert "error" in data, "Resposta não contém a chave 'error'"
    assert "Payload inválido" in data["error"], "Mensagem de erro inesperada para payload inválido"

def test_listar_notificacoes(operador_token, headers):
    """
    Testa a listagem de notificações do operador autenticado.
    """
    response = requests.get(
        f"{BASE_URL}/notificacoes/geral",
        headers={**headers, "Authorization": f"Bearer {operador_token}"},
    )

    assert response.status_code == 200, f"Erro ao listar notificações: {response.text}"
    data = response.json()
    assert "notificacoes" in data, "Resposta não contém a chave 'notificacoes'"
    assert isinstance(data["notificacoes"], list), "O campo 'notificacoes' não é uma lista"


def test_marcar_notificacao_como_lida(chefe_token, operador_token, headers):
    """
    Testa a marcação de uma notificação como lida de forma dinâmica.
    """
    # Criar uma notificação para o teste usando o token do CHEFE DE EQUIPE
    logger.info("Iniciando criação de notificação para o teste...")
    criar_response = requests.post(
        f"{BASE_URL}/notificacoes/notificar-operador",
        headers={**headers, "Authorization": f"Bearer {chefe_token}"},
        json={
            "operador_id": 7,  # Certifique-se de que este ID corresponde a um operador existente no sistema
            "mensagem": "Teste de notificação para marcar como lida."
        },
    )
    print(f"Resposta da API ao criar notificação: {criar_response.json()}")  # Log para depuração
    assert criar_response.status_code == 200, f"Erro ao criar notificação: {criar_response.text}. Verifique se o operador_id é válido e se o chefe_token tem permissão."
    
    notificacao_id = criar_response.json().get("id")
    assert notificacao_id, "ID da notificação não retornado na criação."

    # Testar a marcação da notificação como lida usando o token do OPERADOR
    logger.info(f"Iniciando marcação da notificação {notificacao_id} como lida...")
    response = requests.patch(
        f"{BASE_URL}/notificacoes/{notificacao_id}/marcar-lida",
        headers={**headers, "Authorization": f"Bearer {operador_token}"},
    )
    logger.info(f"Resposta da API ao marcar notificação como lida: {response.status_code}, {response.text}")
    assert response.status_code == 200, f"Erro ao marcar notificação como lida: {response.text}"
    data = response.json()
    assert data["message"] == "Notificação marcada como lida"

    # Limpar a notificação criada para o teste
    logger.info(f"Iniciando exclusão da notificação {notificacao_id} criada para o teste...")
    deletar_response = requests.delete(
        f"{BASE_URL}/notificacoes/{notificacao_id}",
        headers={**headers, "Authorization": f"Bearer {chefe_token}"},
    )
    logger.info(f"Resposta da API ao deletar notificação: {deletar_response.status_code}, {deletar_response.text}")
    assert deletar_response.status_code == 200, f"Erro ao deletar notificação de teste: {deletar_response.text}. Verifique se o chefe_token tem permissão para deletar."


def test_marcar_notificacao_inexistente_como_lida(operador_token, headers):
    """
    Testa a tentativa de marcar uma notificação inexistente como lida.
    """
    notificacao_id = 999  # ID de uma notificação inexistente
    print(f"notificacao_id: {notificacao_id}")  # Adicionando print para depuração
    print(f"headers: {headers}")  # Adicionando print para depuração
    response = requests.patch(
        f"{BASE_URL}/notificacoes/{notificacao_id}/marcar-lida",
        headers={**headers, "Authorization": f"Bearer {operador_token}"},
    )
    print(f"operador_token: {operador_token}")  # Adicionando print para depuração

    assert response.status_code == 404, f"Erro esperado ao marcar notificação inexistente: {response.text}"
    data = response.json()
    assert data["error"] == "Notificação não encontrada ou não pertence ao operador", f"Mensagem de erro inesperada: {data['error']}"

def test_notificar_operador_sem_permissao(operador_token, headers):
    """
    Testa se um usuário sem a permissão 'CHEFE DE EQUIPE' é impedido de acessar a rota.
    """
    response = requests.post(
        f"{BASE_URL}/notificacoes/notificar-operador",
        headers={**headers, "Authorization": f"Bearer {operador_token}"},
        json={"operador_id": 7, "mensagem": "Teste de permissão."},
    )
    assert response.status_code == 403
    data = response.json()  # Chama o método para obter o JSON
    assert data["error"] == "Acesso negado: Permissão insuficiente"