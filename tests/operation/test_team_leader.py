import pytest


def test_listar_operadores(chefe_token, operation_service):
    """
    Testa a listagem de operadores associados ao Chefe de Equipe.
    """
    # Mock do retorno do serviço
    operation_service.listar_operadores.return_value = [
        {"id": 7, "nome": "Operador 1"},
        {"id": 8, "nome": "Operador 2"},
    ]

    operadores = operation_service.listar_operadores(chefe_token)

    assert isinstance(
        operadores, list
    ), "❌ O retorno de 'listar_operadores' deve ser uma lista."
    if operadores:
        operador = operadores[0]
        assert (
            "id" in operador
        ), "❌ O operador retornado não contém o campo obrigatório 'id'."
        assert (
            "nome" in operador
        ), "❌ O operador retornado não contém o campo obrigatório 'nome'."


def test_distribuir_dados(chefe_token, operation_service):
    """
    Testa a distribuição de dados para um Operador.
    """
    operador_id = 7
    quantidade_dados = 50

    # Mock do retorno do serviço
    operation_service.distribuir_dados.return_value = {
        "message": "✅ Dados distribuídos com sucesso.",
        "operador_id": operador_id,
        "quantidade_dados": quantidade_dados,
    }

    resultado = operation_service.distribuir_dados(
        chefe_token, operador_id, quantidade_dados
    )

    assert (
        resultado["message"] == "✅ Dados distribuídos com sucesso."
    ), f"❌ Mensagem inesperada: {resultado['message']}"
    assert (
        resultado["operador_id"] == operador_id
    ), f"❌ O operador_id retornado ({resultado['operador_id']}) não corresponde ao esperado ({operador_id})."
    assert (
        resultado["quantidade_dados"] == quantidade_dados
    ), f"❌ A quantidade de dados retornada ({resultado['quantidade_dados']}) não corresponde ao esperado ({quantidade_dados})."


def test_progresso_operadores(chefe_token, operation_service):
    """
    Testa a visualização do progresso dos Operadores.
    """
    # Mock do retorno do serviço
    operation_service.progresso_operadores.return_value = [
        {
            "operador_id": 7,
            "nome": "Operador 1",
            "dados_distribuidos": 100,
            "dados_restantes": 50,
        }
    ]

    progresso = operation_service.progresso_operadores(chefe_token)

    assert isinstance(
        progresso, list
    ), "❌ O retorno de 'progresso_operadores' deve ser uma lista."
    if progresso:
        operador = progresso[0]
        assert (
            "operador_id" in operador
        ), "❌ O progresso do operador não contém o campo obrigatório 'operador_id'."
        assert (
            "nome" in operador
        ), "❌ O progresso do operador não contém o campo obrigatório 'nome'."
        assert (
            "dados_distribuidos" in operador
        ), "❌ O progresso do operador não contém o campo obrigatório 'dados_distribuidos'."
        assert (
            "dados_restantes" in operador
        ), "❌ O progresso do operador não contém o campo obrigatório 'dados_restantes'."


def test_historico_distribuicao(chefe_token, operation_service):
    """
    Testa o histórico de distribuição de dados para o Chefe de Equipe.
    """
    # Mock do retorno do serviço
    operation_service.obter_historico_distribuicao.return_value = [
        {
            "data_distribuicao": "2025-04-16",
            "operador_id": 7,
            "nome_operador": "Operador 1",
            "dados_distribuidos": 50,
        }
    ]

    historico = operation_service.obter_historico_distribuicao(chefe_token)

    assert isinstance(
        historico, list
    ), "❌ O retorno de 'obter_historico_distribuicao' deve ser uma lista."
    if historico:
        item = historico[0]
        assert (
            "data_distribuicao" in item
        ), "❌ O item do histórico não contém o campo obrigatório 'data_distribuicao'."
        assert (
            "operador_id" in item
        ), "❌ O item do histórico não contém o campo obrigatório 'operador_id'."
        assert (
            "nome_operador" in item
        ), "❌ O item do histórico não contém o campo obrigatório 'nome_operador'."
        assert (
            "dados_distribuidos" in item
        ), "❌ O item do histórico não contém o campo obrigatório 'dados_distribuidos'."


def test_reatribuir_dados_sucesso(chefe_token, operation_service):
    """
    Testa a reatribuição de dados entre dois operadores com sucesso.
    """
    operador_origem_id = 7
    operador_destino_id = 8
    quantidade_dados = 50

    # Mock do retorno do serviço
    operation_service.reatribuir_dados.return_value = {
        "message": "✅ Dados reatribuídos com sucesso.",
        "operador_origem_id": operador_origem_id,
        "operador_destino_id": operador_destino_id,
        "quantidade_dados": quantidade_dados,
    }

    resultado = operation_service.reatribuir_dados(
        chefe_token, operador_origem_id, operador_destino_id, quantidade_dados
    )

    assert (
        resultado["message"] == "✅ Dados reatribuídos com sucesso."
    ), f"❌ Mensagem inesperada: {resultado['message']}"
    assert (
        resultado["operador_origem_id"] == operador_origem_id
    ), f"❌ O operador_origem_id retornado ({resultado['operador_origem_id']}) não corresponde ao esperado ({operador_origem_id})."
    assert (
        resultado["operador_destino_id"] == operador_destino_id
    ), f"❌ O operador_destino_id retornado ({resultado['operador_destino_id']}) não corresponde ao esperado ({operador_destino_id})."
    assert (
        resultado["quantidade_dados"] == quantidade_dados
    ), f"❌ A quantidade de dados retornada ({resultado['quantidade_dados']}) não corresponde ao esperado ({quantidade_dados})."


def test_reatribuir_dados_operador_origem_invalido(chefe_token, operation_service):
    """
    Testa a reatribuição de dados com um operador de origem inválido.
    """
    operador_origem_id = 999
    operador_destino_id = 8
    quantidade_dados = 50

    # Configura o mock para levantar a exceção
    operation_service.reatribuir_dados.side_effect = ValueError(
        "O Operador de origem não pertence ao Chefe de Equipe."
    )

    with pytest.raises(
        ValueError, match="O Operador de origem não pertence ao Chefe de Equipe."
    ):
        operation_service.reatribuir_dados(
            chefe_token, operador_origem_id, operador_destino_id, quantidade_dados
        )


def test_reatribuir_dados_operador_destino_invalido(chefe_token, operation_service):
    """
    Testa a reatribuição de dados com um operador de destino inválido.
    """
    operador_origem_id = 7
    operador_destino_id = 999
    quantidade_dados = 50

    # Configura o mock para levantar a exceção
    operation_service.reatribuir_dados.side_effect = ValueError(
        "O Operador de destino não pertence ao Chefe de Equipe."
    )

    with pytest.raises(
        ValueError, match="O Operador de destino não pertence ao Chefe de Equipe."
    ):
        operation_service.reatribuir_dados(
            chefe_token, operador_origem_id, operador_destino_id, quantidade_dados
        )


def test_reatribuir_dados_quantidade_insuficiente(chefe_token, operation_service):
    """
    Testa a reatribuição de dados com quantidade insuficiente no operador de origem.
    """
    operador_origem_id = 7
    operador_destino_id = 8
    quantidade_dados = 1000

    # Configura o mock para levantar a exceção
    operation_service.reatribuir_dados.side_effect = ValueError(
        "O Operador de origem não possui dados suficientes."
    )

    with pytest.raises(
        ValueError, match="O Operador de origem não possui dados suficientes."
    ):
        operation_service.reatribuir_dados(
            chefe_token, operador_origem_id, operador_destino_id, quantidade_dados
        )


def test_reatribuir_dados_quantidade_negativa(chefe_token, operation_service):
    """
    Testa a reatribuição de dados com quantidade negativa.
    """
    operador_origem_id = 7
    operador_destino_id = 8
    quantidade_dados = -10

    # Configura o mock para levantar a exceção
    operation_service.reatribuir_dados.side_effect = ValueError(
        "A quantidade de dados deve ser um número positivo."
    )

    with pytest.raises(
        ValueError, match="A quantidade de dados deve ser um número positivo."
    ):
        operation_service.reatribuir_dados(
            chefe_token, operador_origem_id, operador_destino_id, quantidade_dados
        )


def test_notificar_operador_sucesso(chefe_token, notification_service):
    """
    Testa o envio de uma notificação para um operador.
    """
    operador_id = 7
    mensagem = "Você recebeu novos dados para processar."

    # Mock do retorno do serviço
    notification_service.notificar_operador.return_value = {
        "message": "✅ Notificação enviada com sucesso.",
        "operador_id": operador_id,
        "mensagem": mensagem,
    }

    resultado = notification_service.notificar_operador(
        chefe_token, operador_id, mensagem
    )

    assert (
        resultado["message"] == "✅ Notificação enviada com sucesso."
    ), f"❌ Mensagem inesperada: {resultado['message']}"
    assert (
        resultado["operador_id"] == operador_id
    ), f"❌ O operador_id retornado ({resultado['operador_id']}) não corresponde ao esperado ({operador_id})."
    assert (
        resultado["mensagem"] == mensagem
    ), f"❌ A mensagem retornada ({resultado['mensagem']}) não corresponde à esperada ({mensagem})."
