import datetime
from flask import Blueprint, jsonify, request # type: ignore
from middlewares.auth_middleware import permission_required, token_required
from flasgger import swag_from # type: ignore
from core.db import get_db_connection

chefe_bp = Blueprint("chefe", __name__, url_prefix="/api/chefe")

@chefe_bp.route("/operadores", methods=["GET"])
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
                                {"id": 1, "nome": "Operador 1", "email": "operador1@example.com"},
                                {"id": 2, "nome": "Operador 2", "email": "operador2@example.com"},
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

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT u.id, u.nome, u.email
        FROM chefe_operadores co
        JOIN usuarios u ON co.operador_id = u.id
        WHERE co.chefe_id = %s
        """,
        (chefe_id,),
    )
    operadores = cursor.fetchall()
    conn.close()

    return jsonify({"operadores": operadores}), 200

@chefe_bp.route("/distribuir-dados", methods=["POST"])
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
        return jsonify({"error": "operador_id e quantidade_dados são obrigatórios"}), 400
    
    # Validação de quantidade
    if quantidade_dados <= 0:
        return jsonify({"error": "A quantidade de dados deve ser um número positivo"}), 400
    
    if quantidade_dados > 500:  # Definindo um limite máximo de 1000 dados por distribuição
        return jsonify({"error": "Não é possível distribuir mais de 150 dados por vez"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Verifica se o Operador pertence ao Chefe de Equipe
    cursor.execute(
        "SELECT 1 FROM chefe_operadores WHERE chefe_id = %s AND operador_id = %s",
        (chefe_id, operador_id),
    )
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"error": "Operador não associado ao Chefe de Equipe"}), 403
    
    # Verifica o total de dados já distribuídos ao operador
    cursor.execute(
        """
        SELECT SUM(dados_restantes) as total_restante
        FROM distribuicao_dados
        WHERE operador_id = %s
        """,
        (operador_id,)
    )
    resultado = cursor.fetchone()
    total_atual = resultado["total_restante"] if resultado and resultado["total_restante"] else 0
    
    # Verifica se o total com a nova distribuição não excede o limite por operador
    limite_por_operador = 5000  # Limite máximo de dados não processados por operador
    if total_atual + quantidade_dados > limite_por_operador:
        cursor.close()
        conn.close()
        return jsonify({
            "error": f"Limite excedido. O operador já possui {total_atual} dados pendentes. Limite máximo: {limite_por_operador}"
        }), 400

    # Insere ou atualiza a distribuição de dados (código existente)
    cursor.execute(
        """
        INSERT INTO distribuicao_dados (chefe_id, operador_id, dados_distribuidos, dados_restantes, data_distribuicao)
        VALUES (%s, %s, %s, %s, NOW())
        ON DUPLICATE KEY UPDATE
        dados_distribuidos = dados_distribuidos + VALUES(dados_distribuidos),
        dados_restantes = dados_restantes + VALUES(dados_restantes)
        """,
        (chefe_id, operador_id, quantidade_dados, quantidade_dados),
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Dados distribuídos com sucesso!"}), 200


@chefe_bp.route("/progresso-operadores", methods=["GET"])
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
                                {"operador_id": 1, "nome": "Operador 1", "dados_distribuidos": 100, "dados_restantes": 50},
                                {"operador_id": 2, "nome": "Operador 2", "dados_distribuidos": 200, "dados_restantes": 30},
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

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT u.id AS operador_id, u.nome, dd.dados_distribuidos, dd.dados_restantes
        FROM distribuicao_dados dd
        JOIN usuarios u ON dd.operador_id = u.id
        WHERE dd.chefe_id = %s
        """,
        (chefe_id,),
    )
    progresso = cursor.fetchall()
    conn.close()

    return jsonify({"progresso": progresso}), 200


@chefe_bp.route("/relatorio-desempenho", methods=["GET"])
@permission_required("CHEFE DE EQUIPE")
@swag_from({
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
            "description": "ID do operador específico (opcional)"
        }
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
                                    {"data": "2023-04-01", "processados": 30, "tempo_processamento": "00:08:45"},
                                    {"data": "2023-04-02", "processados": 25, "tempo_processamento": "00:09:20"}
                                ]
                            }
                        ]
                    }
                }
            }
        },
        403: {
            "description": "Acesso negado. O usuário não tem permissão para acessar esta rota."
        }
    }
})
@token_required
def relatorio_desempenho():
    """
    Fornece um relatório detalhado do desempenho dos operadores associados ao Chefe de Equipe.
    """
    chefe_id = request.user_id
    periodo = request.args.get("periodo", "semana")
    operador_id = request.args.get("operador_id")
    
    # Definir intervalo de datas baseado no período
    hoje = datetime.now().date()
    if periodo == "hoje":
        data_inicio = hoje
        data_fim = hoje
    elif periodo == "mes":
        data_inicio = datetime(hoje.year, hoje.month, 1).date()
        # Último dia do mês atual
        if hoje.month == 12:
            data_fim = datetime(hoje.year + 1, 1, 1).date() - datetime.timedelta(days=1)
        else:
            data_fim = datetime(hoje.year, hoje.month + 1, 1).date() - datetime.timedelta(days=1)
    else:  # semana (padrão)
        # Segunda-feira da semana atual
        data_inicio = hoje - datetime.timedelta(days=hoje.weekday())
        # Domingo da semana atual
        data_fim = data_inicio + datetime.timedelta(days=6)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Filtro de operador específico, se fornecido
    operador_filter = ""
    params = [chefe_id]
    if operador_id:
        operador_filter = " AND dd.operador_id = %s"
        params.append(operador_id)
    
    # Consulta para obter dados de desempenho
    query = f"""
    SELECT 
        u.id AS operador_id, 
        u.nome, 
        u.email,
        dd.dados_distribuidos,
        dd.dados_restantes,
        (dd.dados_distribuidos - dd.dados_restantes) AS dados_processados,
        CASE 
            WHEN dd.dados_distribuidos > 0 
            THEN ((dd.dados_distribuidos - dd.dados_restantes) / dd.dados_distribuidos * 100) 
            ELSE 0 
        END AS eficiencia,
        (
            SELECT AVG(TIMESTAMPDIFF(MINUTE, hr.inicio, hr.fim))
            FROM historico_registros hr
            WHERE hr.operador_id = u.id 
            AND DATE(hr.data_registro) BETWEEN %s AND %s
        ) AS tempo_medio_minutos
    FROM distribuicao_dados dd
    JOIN usuarios u ON dd.operador_id = u.id
    WHERE dd.chefe_id = %s{operador_filter}
    """
    
    cursor.execute(query, [data_inicio, data_fim] + params)
    resultados = cursor.fetchall()
    
    # Para cada operador, buscar detalhes diários
    for operador in resultados:
        cursor.execute("""
            SELECT 
                DATE(hr.data_registro) AS data,
                COUNT(hr.id) AS registros_processados,
                SEC_TO_TIME(AVG(TIMESTAMPDIFF(SECOND, hr.inicio, hr.fim))) AS tempo_medio
            FROM historico_registros hr
            WHERE hr.operador_id = %s
            AND DATE(hr.data_registro) BETWEEN %s AND %s
            GROUP BY DATE(hr.data_registro)
            ORDER BY data
        """, [operador["operador_id"], data_inicio, data_fim])
        
        detalhes_diarios = cursor.fetchall()
        operador["detalhes_diarios"] = detalhes_diarios
        
        # Converter para formato HH:MM:SS
        if operador["tempo_medio_minutos"]:
            horas = int(operador["tempo_medio_minutos"] // 60)
            minutos = int(operador["tempo_medio_minutos"] % 60)
            operador["tempo_medio_processamento"] = f"{horas:02d}:{minutos:02d}:00"
        else:
            operador["tempo_medio_processamento"] = "00:00:00"
        
        # Remover campo temporário
        del operador["tempo_medio_minutos"]
    
    cursor.close()
    conn.close()
    
    return jsonify({
        "periodo": periodo,
        "data_inicio": data_inicio.strftime("%Y-%m-%d"),
        "data_fim": data_fim.strftime("%Y-%m-%d"),
        "desempenho": resultados
    }), 200