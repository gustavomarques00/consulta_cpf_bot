import csv
from io import StringIO
from multiprocessing.connection import Client
from venv import logger
from flask import Blueprint, jsonify, request  # type: ignore
from middlewares.auth_middleware import permission_required, token_required
from flasgger import swag_from  # type: ignore
from core.db import get_db_connection
from core.config import Config
from services import operation_service
from services.extracao_service import ExtracaoService

operacaoes_bp = Blueprint("operacaoes", __name__, url_prefix="/operacaoes")
operation_service = operation_service.OperationService()


@operacaoes_bp.route("/operadores", methods=["GET"])
@token_required
@permission_required("CHEFE DE EQUIPE")
@swag_from(
    {
        "tags": ["Chefe de Equipe"],
        "summary": "Listar Operadores",
        "description": "Lista os operadores associados ao Chefe de Equipe autenticado.",
        "responses": {
            200: {
                "description": "Lista de operadores associados ao Chefe de Equipe.",
                "content": {
                    "application/json": {
                        "example": {
                            "operadores": [
                                {
                                    "id": 1,
                                    "nome": "Operador 1",
                                    "email": "operador1@example.com",
                                },
                                {
                                    "id": 2,
                                    "nome": "Operador 2",
                                    "email": "operador2@example.com",
                                },
                            ]
                        }
                    }
                },
            },
            403: {
                "description": "Acesso negado. O usuário não tem permissão para acessar esta rota.",
            },
        },
    }
)
def listar_operadores():
    """
    Lista os operadores associados ao Chefe de Equipe autenticado.
    """
    chefe_id = request.user_id  # ID do Chefe de Equipe autenticado

    try:
        logger.info(f"Usuário {chefe_id} iniciou consulta de operadores.")
        operadores = operation_service.listar_operadores(chefe_id)
        logger.info(
            f"Consulta de operadores concluída com sucesso para o usuário {chefe_id}."
        )
        return jsonify({"operadores": operadores}), 200
    except Exception as e:
        logger.error(f"Erro ao listar operadores para o usuário {chefe_id}: {str(e)}")
        return jsonify({"error": f"Erro ao listar operadores: {str(e)}"}), 500


@operacaoes_bp.route("/distribuir-dados", methods=["POST"])
@permission_required("CHEFE DE EQUIPE")
@swag_from(
    {
        "tags": ["Chefe de Equipe"],
        "summary": "Distribuir dados para um Operador",
        "description": "Permite ao Chefe de Equipe distribuir dados para um Operador.",
        "parameters": [
            {
                "name": "operador_id",
                "in": "query",
                "type": "integer",
                "required": True,
                "description": "ID do Operador para o qual os dados serão distribuídos.",
            },
            {
                "name": "quantidade_dados",
                "in": "query",
                "type": "integer",
                "required": True,
                "description": "Quantidade de dados a ser distribuída.",
            },
        ],
    }
)
@token_required
def distribuir_dados():
    """
    Permite ao Chefe de Equipe distribuir dados para um Operador.
    """
    chefe_id = request.user_id
    data = request.get_json()
    operador_id = data.get("operador_id")
    quantidade_dados = data.get("quantidade_dados")

    if not operador_id or not quantidade_dados:
        return (
            jsonify({"error": "operador_id e quantidade_dados são obrigatórios"}),
            400,
        )

    try:
        logger.info(
            f"Usuário {chefe_id} iniciou distribuição de dados para o operador {operador_id}."
        )
        operation_service.distribuir_dados(chefe_id, operador_id, quantidade_dados)
        logger.info(
            f"Distribuição de dados concluída com sucesso para o operador {operador_id}."
        )
        return jsonify({"message": "Dados distribuídos com sucesso!"}), 200
    except ValueError as e:
        logger.warning(f"Erro de validação ao distribuir dados: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except PermissionError as e:
        logger.warning(f"Erro de permissão ao distribuir dados: {str(e)}")
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        logger.error(f"Erro ao distribuir dados: {str(e)}")
        return jsonify({"error": f"Erro ao distribuir dados: {str(e)}"}), 500


@operacaoes_bp.route("/progresso-operadores", methods=["GET"])
@permission_required("CHEFE DE EQUIPE")
@swag_from(
    {
        "tags": ["Chefe de Equipe"],
        "summary": "Progresso dos Operadores",
        "description": "Retorna o progresso de cada Operador (dados processados/restantes).",
        "responses": {
            200: {
                "description": "Progresso dos operadores.",
                "content": {
                    "application/json": {
                        "example": {
                            "progresso": [
                                {
                                    "operador_id": 1,
                                    "nome": "Operador 1",
                                    "dados_distribuidos": 100,
                                    "dados_restantes": 50,
                                },
                                {
                                    "operador_id": 2,
                                    "nome": "Operador 2",
                                    "dados_distribuidos": 200,
                                    "dados_restantes": 30,
                                },
                            ]
                        }
                    }
                },
            },
            403: {
                "description": "Acesso negado. O usuário não tem permissão para acessar esta rota.",
            },
        },
    }
)
@token_required
def progresso_operadores():
    """
    Retorna o progresso de cada Operador (dados processados/restantes).
    """
    chefe_id = request.user_id  # ID do Chefe de Equipe autenticado

    try:
        logger.info(f"Usuário {chefe_id} iniciou consulta de progresso dos operadores.")
        progresso = operation_service.progresso_operadores(chefe_id)
        logger.info(
            f"Consulta de progresso concluída com sucesso para o usuário {chefe_id}."
        )
        return jsonify({"progresso": progresso}), 200
    except Exception as e:
        logger.error(f"Erro ao consultar progresso dos operadores: {str(e)}")
        return (
            jsonify({"error": f"Erro ao consultar progresso dos operadores: {str(e)}"}),
            500,
        )


@operacaoes_bp.route("/relatorio-desempenho", methods=["GET"])
@permission_required("CHEFE DE EQUIPE")
@swag_from(
    {
        "tags": ["Chefe de Equipe"],
        "summary": "Relatório de Desempenho dos Operadores",
        "description": "Fornece um relatório detalhado do desempenho dos operadores associados ao Chefe de Equipe.",
        "parameters": [
            {
                "name": "periodo",
                "in": "query",
                "type": "string",
                "required": False,
                "description": "Período do relatório: 'hoje', 'semana', 'mes'. Padrão é 'semana'.",
            },
            {
                "name": "operador_id",
                "in": "query",
                "type": "integer",
                "required": False,
                "description": "ID do operador específico (opcional)",
            },
        ],
        "responses": {
            200: {
                "description": "Relatório de desempenho dos operadores.",
                "content": {
                    "application/json": {
                        "example": {
                            "periodo": "semana",
                            "data_inicio": "2023-04-01",
                            "data_fim": "2023-04-07",
                            "desempenho": [
                                {
                                    "operador_id": 1,
                                    "nome": "Operador 1",
                                    "email": "operador1@example.com",
                                    "dados_processados": 150,
                                    "dados_pendentes": 50,
                                    "eficiencia": 75.0,
                                    "tempo_medio_processamento": "00:10:30",
                                    "detalhes_diarios": [
                                        {
                                            "data": "2023-04-01",
                                            "processados": 30,
                                            "tempo_processamento": "00:08:45",
                                        },
                                        {
                                            "data": "2023-04-02",
                                            "processados": 25,
                                            "tempo_processamento": "00:09:20",
                                        },
                                    ],
                                }
                            ],
                        }
                    }
                },
            },
            403: {
                "description": "Acesso negado. O usuário não tem permissão para acessar esta rota."
            },
        },
    }
)
@token_required
def relatorio_desempenho():
    """
    Fornece um relatório detalhado do desempenho dos operadores associados ao Chefe de Equipe.
    """
    chefe_id = request.user_id
    periodo = request.args.get("periodo", "semana")
    operador_id = request.args.get("operador_id")

    try:
        logger.info(f"Usuário {chefe_id} iniciou consulta de relatório de desempenho.")
        response = operation_service.gerar_relatorio_desempenho(
            chefe_id, periodo, operador_id
        )
        logger.info(
            f"Relatório de desempenho gerado com sucesso para o usuário {chefe_id}."
        )
        return jsonify(response), 200
    except ValueError as e:
        logger.warning(f"Erro de validação ao gerar relatório: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Erro ao gerar relatório de desempenho: {str(e)}")
        return (
            jsonify({"error": f"Erro ao gerar relatório de desempenho: {str(e)}"}),
            500,
        )


@operacaoes_bp.route("/historico-distribuicao", methods=["GET"])
@permission_required("CHEFE DE EQUIPE")
@swag_from(
    {
        "tags": ["Chefe de Equipe"],
        "summary": "Histórico de Distribuição de Dados",
        "description": "Lista o histórico de distribuições realizadas pelo Chefe de Equipe para seus Operadores.",
        "responses": {
            200: {
                "description": "Histórico de distribuições realizadas.",
                "content": {
                    "application/json": {
                        "example": {
                            "historico": [
                                {
                                    "data_distribuicao": "2023-04-07",
                                    "operador_id": 1,
                                    "nome_operador": "Operador 1",
                                    "dados_distribuidos": 100,
                                },
                                {
                                    "data_distribuicao": "2023-04-06",
                                    "operador_id": 2,
                                    "nome_operador": "Operador 2",
                                    "dados_distribuidos": 150,
                                },
                            ]
                        }
                    }
                },
            },
            403: {
                "description": "Acesso negado. O usuário não tem permissão para acessar esta rota.",
            },
        },
    }
)
@token_required
def historico_distribuicao():
    """
    Lista o histórico de distribuições realizadas pelo Chefe de Equipe para seus Operadores.
    """
    chefe_id = request.user_id  # ID do Chefe de Equipe autenticado

    try:
        logger.info(
            f"Usuário {chefe_id} iniciou consulta do histórico de distribuição."
        )
        historico = operation_service.obter_historico_distribuicao(chefe_id)
        logger.info(
            f"Consulta do histórico de distribuição concluída com sucesso para o usuário {chefe_id}."
        )
        return jsonify({"historico": historico}), 200
    except Exception as e:
        logger.error(f"Erro ao consultar histórico de distribuição: {str(e)}")
        return (
            jsonify(
                {"error": f"Erro ao consultar histórico de distribuição: {str(e)}"}
            ),
            500,
        )


@operacaoes_bp.route("/reatribuir-dados", methods=["POST"])
@permission_required("CHEFE DE EQUIPE")
@swag_from(
    {
        "tags": ["Chefe de Equipe"],
        "summary": "Reatribuir Dados entre Operadores",
        "description": "Permite ao Chefe de Equipe reatribuir dados não processados de um Operador para outro.",
        "parameters": [
            {
                "name": "operador_origem_id",
                "in": "query",
                "type": "integer",
                "required": True,
                "description": "ID do Operador de origem dos dados.",
            },
            {
                "name": "operador_destino_id",
                "in": "query",
                "type": "integer",
                "required": True,
                "description": "ID do Operador de destino dos dados.",
            },
            {
                "name": "quantidade_dados",
                "in": "query",
                "type": "integer",
                "required": True,
                "description": "Quantidade de dados a ser reatribuída.",
            },
        ],
        "responses": {
            200: {
                "description": "Reatribuição realizada com sucesso.",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "✅ Dados reatribuídos com sucesso.",
                            "operador_origem_id": 1,
                            "operador_destino_id": 2,
                            "quantidade_dados": 50,
                        }
                    }
                },
            },
            400: {
                "description": "Erro de validação ou dados insuficientes.",
            },
            403: {
                "description": "Acesso negado. O usuário não tem permissão para acessar esta rota.",
            },
        },
    }
)
@token_required
def reatribuir_dados():
    """
    Permite ao Chefe de Equipe reatribuir dados não processados de um Operador para outro.
    """
    chefe_id = request.user_id
    data = request.get_json()
    operador_origem_id = data.get("operador_origem_id")
    operador_destino_id = data.get("operador_destino_id")
    quantidade_dados = data.get("quantidade_dados")

    if not operador_origem_id or not operador_destino_id or not quantidade_dados:
        return (
            jsonify(
                {
                    "error": "operador_origem_id, operador_destino_id e quantidade_dados são obrigatórios"
                }
            ),
            400,
        )

    if quantidade_dados <= 0:
        return (
            jsonify({"error": "A quantidade de dados deve ser um número positivo"}),
            400,
        )

    try:
        logger.info(
            f"Usuário {chefe_id} iniciou reatribuição de dados de {operador_origem_id} para {operador_destino_id}."
        )
        operation_service.reatribuir_dados(
            chefe_id, operador_origem_id, operador_destino_id, quantidade_dados
        )
        logger.info(f"Reatribuição concluída com sucesso para o usuário {chefe_id}.")
        return (
            jsonify(
                {
                    "message": "✅ Dados reatribuídos com sucesso.",
                    "operador_origem_id": operador_origem_id,
                    "operador_destino_id": operador_destino_id,
                    "quantidade_dados": quantidade_dados,
                }
            ),
            200,
        )
    except ValueError as e:
        logger.warning(f"Erro de validação ao reatribuir dados: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except PermissionError as e:
        logger.warning(f"Erro de permissão ao reatribuir dados: {str(e)}")
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        logger.error(f"Erro ao reatribuir dados: {str(e)}")
        return jsonify({"error": f"Erro ao reatribuir dados: {str(e)}"}), 500


@operacaoes_bp.route("/upload-cpfs", methods=["POST"])
@swag_from(
    {
        "tags": ["Chefe de Equipe"],
        "summary": "Upload de CPFs para processamento",
        "description": "Permite ao Chefe de Equipe enviar um arquivo CSV com CPFs para processamento e escolher os campos desejados.",
        "parameters": [
            {
                "name": "file",
                "in": "formData",
                "type": "file",
                "required": True,
                "description": "Arquivo CSV contendo uma coluna 'cpf'.",
            },
            {
                "name": "campos",
                "in": "query",
                "type": "array",
                "items": {"type": "string"},
                "required": True,
                "description": "Lista de campos desejados (ex.: NOME, CPF, SEXO, NASCIMENTO, RENDA, PODER_AQUISITIVO, EMAIL, TELEFONES).",
            },
            {
                "name": "status_inicial",
                "in": "query",
                "type": "string",
                "required": False,
                "description": "Status inicial dos leads: Criar, Criado ou Recusado. Padrão: Criar.",
            },
        ],
        "responses": {
            200: {"description": "Arquivo processado com sucesso."},
            400: {"description": "Erro de validação ou arquivo inválido."},
            500: {"description": "Erro interno do servidor."},
        },
    }
)
@token_required
@permission_required("CHEFE DE EQUIPE")
def upload_cpfs():
    """
    Permite ao Chefe de Equipe enviar um arquivo com CPFs para processamento e escolher os campos desejados.
    """
    chefe_id = request.user_id
    logger.info(f"Usuário {chefe_id} iniciou upload de CPFs.")

    if "file" not in request.files:
        logger.warning(f"Usuário {chefe_id} não enviou nenhum arquivo.")
        return jsonify({"error": "Nenhum arquivo enviado."}), 400

    file = request.files["file"]
    if file.filename == "":
        logger.warning(f"Usuário {chefe_id} enviou um arquivo com nome vazio.")
        return jsonify({"error": "O nome do arquivo está vazio."}), 400

    if not file.filename.endswith(".csv"):
        logger.warning(
            f"Usuário {chefe_id} enviou um arquivo com extensão inválida: {file.filename}."
        )
        return jsonify({"error": "Apenas arquivos CSV são suportados."}), 400

    try:
        # Processar o arquivo CSV
        logger.info(
            f"Usuário {chefe_id} enviou o arquivo {file.filename} para processamento."
        )
        csv_data = StringIO(file.stream.read().decode("utf-8"))
        reader = csv.reader(csv_data)
        header = next(reader)

        if "cpf" not in [col.lower() for col in header]:
            logger.warning(f"Usuário {chefe_id} enviou um arquivo sem a coluna 'cpf'.")
            return jsonify({"error": "O arquivo deve conter uma coluna 'cpf'."}), 400

        cpfs = [row[0].strip() for row in reader if row]
        logger.info(
            f"Usuário {chefe_id} enviou um arquivo com {len(cpfs)} CPFs para processamento."
        )

        # Validação dos campos desejados
        campos_desejados = request.args.get("campos", "").split(",")
        logger.debug(f"Campos recebidos: {campos_desejados}")
        campos_permitidos = ExtracaoService(Config).CAMPOS_PERMITIDOS
        if not all(
            campo.strip() in campos_permitidos
            for campo in campos_desejados
            if campo.strip()
        ):
            logger.warning(
                f"Usuário {chefe_id} enviou campos inválidos: {campos_desejados}."
            )
            return jsonify({"error": "Campos inválidos"}), 400

        status_inicial = request.args.get("status_inicial", "Criar")

        logger.info(
            f"Usuário {chefe_id} selecionou os campos: {campos_desejados} e status inicial: {status_inicial}."
        )
        resultados = operation_service.processar_cpfs_upload(
            chefe_id, cpfs, campos_desejados, status_inicial
        )

        logger.info(
            f"Processamento do arquivo enviado pelo usuário {chefe_id} concluído com sucesso."
        )
        return (
            jsonify(
                {"message": "Arquivo processado com sucesso.", "resultados": resultados}
            ),
            200,
        )

    except Exception as e:
        logger.error(
            f"Erro ao processar o arquivo enviado pelo usuário {chefe_id}: {str(e)}"
        )
        return jsonify({"error": f"Erro ao processar o arquivo: {str(e)}"}), 500
