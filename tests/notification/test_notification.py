import pytest
from backend.services.notification_service import NotificationService
from core.config import Config
from unittest.mock import patch, MagicMock

# Instância do serviço de notificações
notification_service = NotificationService()


def test_notificar_operador_erro_interno():
    """
    Testa o envio de notificação para um operador quando ocorre um erro interno.
    Para simular o erro, forçamos uma exceção na obtenção da conexão com o banco.
    """
    chefe_id = 1  # ID do chefe (presumivelmente válido)
    operador_id = 7  # ID do operador válido
    mensagem = "Teste de erro interno."

    # Força uma exceção na função get_db_connection usada pelo serviço
    with patch(
        "backend.services.notification_service.get_db_connection",
        side_effect=Exception("Erro simulado"),
    ):
        result, status = notification_service.notificar_operador(
            chefe_id, operador_id, mensagem
        )
        assert status == 500, f"Esperado status 500, mas obteve {status}"
        assert "error" in result, "Resposta não contém a chave 'error'"
        assert "Erro ao salvar notificação no sistema interno:" in result["error"]


def test_notificar_operador_sem_autorizacao():
    """
    Testa se o envio de notificação retorna erro quando o operador não está associado ao chefe.
    """
    chefe_id = 1
    operador_id = 9999  # ID que não está associado
    mensagem = "Teste de permissão."

    result, status = notification_service.notificar_operador(
        chefe_id, operador_id, mensagem
    )
    assert status == 403, f"Esperado status 403, mas obteve {status}"
    assert "error" in result, "Resposta não contém a chave 'error'"
    assert result["error"] == "Operador não associado ao Chefe de Equipe"


def test_notificar_operador_payload_invalido():
    """
    Testa o envio de notificação com payload inválido.
    Caso os tipos estejam incorretos, o serviço retorna 403 com mensagem de erro.
    """
    chefe_id = 1
    result, status = notification_service.notificar_operador(
        chefe_id, "invalid_id", 12345
    )
    assert status == 403, f"Esperado status 403, mas obteve {status}"
    assert "error" in result, "Resposta não contém a chave 'error'"
    assert result["error"] == "Operador não associado ao Chefe de Equipe"


def test_listar_notificacoes():
    """
    Testa a listagem das notificações de um operador.
    """
    operador_id = 7
    result, status = notification_service.listar_notificacoes(operador_id)
    assert status == 200, f"Erro ao listar notificações: status {status}"
    assert "notificacoes" in result, "Resposta não contém a chave 'notificacoes'"
    assert isinstance(
        result["notificacoes"], list
    ), "O campo 'notificacoes' não é uma lista"


def test_marcar_notificacao_como_lida():
    """
    Testa a marcação de uma notificação como lida.
    Cria uma notificação, marca-a como lida e depois a deleta.
    """
    chefe_id = 1
    operador_id = 7
    mensagem = "Teste para marcar como lida."

    # Cria a notificação
    criar_result, criar_status = notification_service.notificar_operador(
        chefe_id, operador_id, mensagem
    )
    assert criar_status == 200, f"Erro ao criar notificação: {criar_result}"
    notificacao_id = criar_result.get("id")
    assert notificacao_id, "ID da notificação não retornado"

    # Marca como lida
    marcar_result, marcar_status = notification_service.marcar_notificacao_como_lida(
        operador_id, notificacao_id
    )
    assert (
        marcar_status == 200
    ), f"Erro ao marcar notificação como lida: {marcar_result}"
    assert marcar_result.get("message") == "Notificação marcada como lida"

    # Deleta a notificação para limpeza
    deletar_result, deletar_status = notification_service.deletar_notificacao(
        chefe_id, notificacao_id
    )
    assert deletar_status == 200, f"Erro ao deletar notificação: {deletar_result}"


def test_marcar_notificacao_inexistente_como_lida():
    """
    Testa a tentativa de marcar uma notificação inexistente como lida.
    """
    operador_id = 7
    notificacao_id = 999  # ID inexistente
    result, status = notification_service.marcar_notificacao_como_lida(
        operador_id, notificacao_id
    )
    assert status == 404, f"Esperado status 404, mas obteve {status}"
    assert "error" in result, "Resposta não contém a chave 'error'"
    assert result["error"] == "Notificação não encontrada ou não pertence ao operador"


def test_notificar_operador_sem_permissao():
    """
    Testa se um chefe que não tem permissão para notificar determinada ação
    tem a operação bloqueada. Simula que o operador não está associado.
    """
    chefe_id = 1
    operador_id = 8  # Supondo que o operador 8 não esteja associado ao chefe 1
    mensagem = "Teste de permissão."

    # Patch na função get_db_connection para simular que a consulta não encontrou associação
    with patch(
        "backend.services.notification_service.get_db_connection"
    ) as mock_get_db_conn:
        fake_conn = MagicMock()
        fake_cursor = MagicMock()
        fake_cursor.fetchone.return_value = None  # Simula ausência de associação
        fake_conn.cursor.return_value = fake_cursor
        mock_get_db_conn.return_value = fake_conn

        result, status = notification_service.notificar_operador(
            chefe_id, operador_id, mensagem
        )
        assert status == 403, f"Esperado status 403, mas obteve {status}"
        assert "error" in result, "Resposta não contém 'error'"
        assert result["error"] == "Operador não associado ao Chefe de Equipe"
