from flask import Blueprint, jsonify, request  # type: ignore
from core.db import get_db_connection
from middlewares.auth_middleware import token_required, only_super_admin
import json
import datetime
from utils.token import generate_token, create_refresh_token, generate_tokens
import jwt  # type: ignore
from utils.parse_date import parse_date
import os

plans_bp = Blueprint("plans_bp", __name__)

JWT_SECRET = os.getenv("JWT_SECRET", "secretdoapp")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


@plans_bp.route("/api/plans", methods=["GET"])
def get_plans():
    """
    Retorna a lista de todos os planos disponíveis.
    ---
    tags:
      - Planos
    responses:
      200:
        description: Lista de planos com id, nome, preço e features
      404:
        description: Nenhum plano encontrado
      500:
        description: Erro ao consultar o banco
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, preco, features FROM planos")
        plans = cursor.fetchall()
        for plan in plans:
            if isinstance(plan["features"], str):
                plan["features"] = json.loads(plan["features"])
            elif not isinstance(plan["features"], list):
                plan["features"] = []
        conn.close()

        if not plans:
            return jsonify({"error": "Nenhum plano encontrado!"}), 404

        return jsonify(plans), 200
    except Exception as err:
        return jsonify({"error": str(err)}), 500


@plans_bp.route("/api/user-plans", methods=["GET"])
@token_required
def get_user_plan():
    """
    Retorna o plano associado ao usuário autenticado via token.
    ---
    tags:
      - Planos
    security:
      - Bearer: []
    responses:
      200:
        description: Detalhes do plano do usuário
      401:
        description: Token inválido ou ausente
      404:
        description: Plano não encontrado para o usuário
    """
    user_id = request.user_id
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT p.id, p.nome, p.preco, p.features, up.data_inicio, up.data_fim
        FROM usuarios_planos up 
        JOIN planos p ON up.plano_id = p.id 
        WHERE up.usuario_id = %s
        """,
        (user_id,),
    )
    user_plan = cursor.fetchone()
    conn.close()

    if not user_plan:
        return jsonify({"error": "Plano não encontrado!"}), 404

    # Formatar as datas no padrão brasileiro usando parse_date
    if user_plan["data_inicio"]:
        user_plan["data_inicio"] = parse_date(str(user_plan["data_inicio"]))
    if user_plan["data_fim"]:
        user_plan["data_fim"] = parse_date(str(user_plan["data_fim"]))

    return jsonify(user_plan), 200


@plans_bp.route("/api/generate-token", methods=["POST"])
def generate_and_store_token():
    """
    Gera e armazena um token JWT vinculado ao usuário e plano.
    ---
    tags:
      - Autenticação
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            user_id:
              type: integer
              example: 4
            cargo:
              type: string
              example: ADM
    responses:
      200:
        description: Token gerado e armazenado com sucesso
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Token gerado com sucesso!"
            token:
              type: string
              example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            refresh_token:
              type: string
              example: "d3f9a2a9-09e3-4f6d-a89b-5b91f03dcff2"
      400:
        description: user_id ausente
        schema:
          type: object
          properties:
            error:
              type: string
              example: "user_id é obrigatório!"
      404:
        description: Plano do usuário não encontrado
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Plano não encontrado!"
      500:
        description: Erro no banco de dados
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Erro interno ao gerar token."
    """
    try:
        data = request.get_json()
        if not data or "user_id" not in data:
            return jsonify({"error": "user_id é obrigatório!"}), 400

        user_id = data["user_id"]
        cargo = data.get("cargo", "Independente")

        tokens = generate_tokens(user_id, cargo)
        access_token, refresh_token = tokens["access_token"], tokens["refresh_token"]

        # Conectar ao banco
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Verificar plano do usuário
        cursor.execute(
            "SELECT plano_id FROM usuarios_planos WHERE usuario_id = %s", (user_id,)
        )
        user_plan = cursor.fetchone()

        if not user_plan:
            return jsonify({"error": "Plano não encontrado!"}), 404

        # Definir expiração (7 dias)
        expira_em = datetime.datetime.utcnow() + datetime.timedelta(days=7)

        # Salvar refresh token
        cursor.execute("DELETE FROM refresh_tokens WHERE usuario_id = %s", (user_id,))
        cursor.execute(
            "INSERT INTO refresh_tokens (usuario_id, token, expira_em) VALUES (%s, %s, %s)",
            (user_id, refresh_token, expira_em),
        )
        conn.commit()

        return (
            jsonify(
                {
                    "message": "Token gerado com sucesso!",
                    "token": access_token,
                    "refresh_token": refresh_token,
                }
            ),
            200,
        )

    except KeyError as e:
        return jsonify({"error": f"Campo obrigatório ausente: {str(e)}"}), 400
    except Exception as err:
        conn.rollback()
        return jsonify({"error": "Erro interno ao gerar token."}), 500
    finally:
        if conn:
            conn.close()


@plans_bp.route("/api/superadmin/test", methods=["GET"])
@token_required
@only_super_admin
def test_superadmin():
    """
    Rota de teste exclusiva para usuários com cargo ADM (superadmin).
    ---
    tags:
      - Administração
    security:
      - Bearer: []
    responses:
      200:
        description: Acesso liberado ao super admin
      403:
        description: Acesso negado para usuários comuns
      401:
        description: Token ausente ou inválido
    """
    return jsonify({"message": f"Acesso liberado, Super Admin {request.user_id}!"})


@plans_bp.route("/api/refresh-token", methods=["POST"])
def refresh_token():
    """
    Gera um novo token de acesso com base no Refresh Token enviado via header.
    ---
    tags:
      - Autenticação
    parameters:
      - in: header
        name: Refresh-Token
        required: true
        type: string
        description: Token de renovação (válido por 30 dias)
    responses:
      200:
        description: Novo token JWT gerado com sucesso
        schema:
          type: object
          properties:
            token:
              type: string
              example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
      401:
        description: Refresh token ausente, expirado ou inválido
    """
    refresh_token = request.headers.get("Refresh-Token")
    if not refresh_token:
        return jsonify({"error": "Refresh token ausente!"}), 401

    try:
        # Decodifica o refresh token
        data = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = data["user_id"]

        # Gera novo token com 2 horas de validade
        novo_token = generate_token(user_id=user_id, cargo=data.get("cargo", "Usuario"))

        return jsonify({"token": novo_token}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Refresh token expirado!"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Refresh token inválido!"}), 401


@plans_bp.route("/api/revoke-token", methods=["POST"])
@token_required
@only_super_admin
def revoke_token():
    """
    Revoga um access_token manualmente (blacklist).
    ---
    tags:
      - Administração
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            token:
              type: string
              example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    responses:
      200:
        description: Token revogado com sucesso
      400:
        description: Token ausente
    """
    data = request.get_json()
    access_token = data.get("token")

    if not access_token:
        return jsonify({"error": "Access token ausente!"}), 400

    # Inserir o token na blacklist
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO token_blacklist (token, invalidado_em) VALUES (%s, %s)",
        (access_token, datetime.datetime.utcnow()),
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Access token revogado com sucesso!"}), 200


@plans_bp.route("/api/admin/refresh-tokens", methods=["GET"])
@token_required
@only_super_admin
def listar_refresh_tokens():
    """
    Lista todos os refresh tokens com paginação e filtros opcionais.
    ---
    tags:
      - Administração
    parameters:
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: limit
        type: integer
        default: 10
      - in: query
        name: email
        type: string
        required: false
        description: Filtrar pelo email do usuário
      - in: query
        name: revogado
        type: boolean
        required: false
        description: Filtrar por status de revogação
    responses:
      200:
        description: Tokens paginados com total_pages
    """
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    email_filter = request.args.get("email")
    revogado_filter = request.args.get("revogado")

    offset = (page - 1) * limit

    base_query = """
        FROM refresh_tokens rt
        JOIN usuarios u ON rt.usuario_id = u.id
        WHERE 1=1
    """
    params = []

    if email_filter:
        base_query += " AND u.email LIKE %s"
        params.append(f"%{email_filter}%")

    if revogado_filter in ["true", "false"]:
        base_query += " AND rt.revogado = %s"
        params.append(revogado_filter.lower() == "true")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Total de resultados
    cursor.execute(f"SELECT COUNT(*) AS total {base_query}", params)
    total = cursor.fetchone()["total"]
    total_pages = (total + limit - 1) // limit

    # Resultados paginados
    cursor.execute(
        f"""
        SELECT rt.id, rt.token, rt.criado_em, rt.expira_em, rt.revogado,
               u.id as usuario_id, u.email
        {base_query}
        ORDER BY rt.criado_em DESC
        LIMIT %s OFFSET %s
    """,
        (*params, limit, offset),
    )
    tokens = cursor.fetchall()

    return (
        jsonify(
            {
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "total_results": total,
                "data": tokens,
            }
        ),
        200,
    )


@plans_bp.route("/api/admin/token-blacklist", methods=["GET"])
@token_required
@only_super_admin
def listar_tokens_revogados():
    """
    Lista tokens de access revogados (paginado).
    ---
    tags:
      - Administração
    parameters:
      - in: query
        name: page
        type: integer
        default: 1
        required: false
      - in: query
        name: limit
        type: integer
        default: 10
        required: false
    responses:
      200:
        description: Lista paginada de tokens revogados
    """
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    offset = (page - 1) * limit

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, token, invalidado_em
        FROM token_blacklist
        ORDER BY invalidado_em DESC
        LIMIT %s OFFSET %s
    """,
        (limit, offset),
    )
    tokens = cursor.fetchall()
    return jsonify(tokens), 200


@plans_bp.route("/api/admin/revoke-refresh-token", methods=["POST"])
@token_required
@only_super_admin
def revogar_refresh_token():
    """
    Revoga um refresh token específico.
    ---
    tags:
      - Administração
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            token:
              type: string
              example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    responses:
      200:
        description: Refresh token revogado com sucesso
      400:
        description: Token ausente
    """
    data = request.get_json()
    refresh_token = data.get("refresh_token")

    if not refresh_token:
        return jsonify({"error": "Refresh token ausente!"}), 400

    # Atualizar o status do refresh token
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE refresh_tokens SET revogado = TRUE WHERE token = %s", (refresh_token,)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Refresh token revogado com sucesso!"}), 200
