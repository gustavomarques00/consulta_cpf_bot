from flask import Blueprint, jsonify, request
from utils.db import get_db_connection
from middlewares.auth import token_required, only_super_admin
import json
import datetime
from utils.token import decode_token, generate_token, create_refresh_token
import jwt

plans_bp = Blueprint('plans_bp', __name__)

@plans_bp.route('/api/plans', methods=['GET'])
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
            if isinstance(plan['features'], str):
                plan['features'] = json.loads(plan['features'])
            elif not isinstance(plan['features'], list):
                plan['features'] = []
        conn.close()

        if not plans:
            return jsonify({"error": "Nenhum plano encontrado!"}), 404

        return jsonify(plans), 200
    except Exception as err:
        return jsonify({"error": str(err)}), 500

@plans_bp.route('/api/user-plans', methods=['GET'])
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
    cursor.execute("""
        SELECT p.id, p.nome, p.preco, p.features 
        FROM usuarios_planos up 
        JOIN planos p ON up.plano_id = p.id 
        WHERE up.usuario_id = %s
    """, (user_id,))
    user_plan = cursor.fetchone()
    conn.close()

    if not user_plan:
        return jsonify({"error": "Plano não encontrado!"}), 404

    return jsonify(user_plan), 200

@plans_bp.route('/api/generate-token', methods=['POST'])
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
      400:
        description: user_id ausente
      404:
        description: Plano do usuário não encontrado
      500:
        description: Erro no banco de dados
    """
    data = request.get_json()
    user_id = data.get('user_id')
    cargo = data.get('cargo', 'Independente')

    if not user_id:
        return jsonify({"error": "user_id é obrigatório!"}), 400

    tokens = generate_tokens(user_id, cargo)
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT plano_id FROM usuarios_planos WHERE usuario_id = %s", (user_id,))
    user_plan = cursor.fetchone()

    if not user_plan:
        return jsonify({"error": "Plano não encontrado!"}), 404

    plano_id = user_plan['plano_id']

    # Cálculo de expiração (7 dias)
    expira_em = datetime.datetime.utcnow() + datetime.timedelta(days=7)

    try:
        # Salvar refresh token em nova tabela
        cursor.execute(
            "INSERT INTO refresh_tokens (usuario_id, token, expira_em) VALUES (%s, %s, %s)",
            (user_id, tokens["refresh_token"], expira_em)
        )
        conn.commit()
        conn.close()
        return jsonify({
            "message": "Token gerado com sucesso!",
            "token": token
        }), 200
    except Exception as err:
        conn.rollback()
        conn.close()
        return jsonify({"error": str(err)}), 500

@plans_bp.route('/api/superadmin/test', methods=['GET'])
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

@plans_bp.route('/api/refresh-token', methods=['POST'])
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
    refresh_token = request.headers.get('Refresh-Token')
    if not refresh_token:
        return jsonify({"error": "Refresh token ausente!"}), 401

    try:
        # Decodifica o refresh token
        data = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = data['user_id']

        # Gera novo token com 2 horas de validade
        novo_token = generate_token(user_id=user_id, cargo=data.get("cargo", "Usuario"))

        return jsonify({"token": novo_token}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Refresh token expirado!"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Refresh token inválido!"}), 401

@plans_bp.route('/api/revoke-token', methods=['POST'])
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
    token = data.get("token")

    if not token:
        return jsonify({"error": "Token ausente!"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO token_blacklist (token) VALUES (%s)", (token,))
    conn.commit()

    return jsonify({"message": "Token revogado com sucesso!"}), 200

@plans_bp.route('/api/admin/refresh-tokens', methods=['GET'])
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
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    email_filter = request.args.get('email')
    revogado_filter = request.args.get('revogado')

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
    
    if revogado_filter in ['true', 'false']:
        base_query += " AND rt.revogado = %s"
        params.append(revogado_filter.lower() == 'true')

    # Total count para paginação
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT COUNT(*) AS total {base_query}", params)
    total = cursor.fetchone()['total']
    total_pages = (total + limit - 1) // limit

    # Query final paginada
    cursor.execute(f"""
        SELECT rt.id, rt.token, rt.criado_em, rt.expira_em, rt.revogado,
               u.id as usuario_id, u.email
        {base_query}
        ORDER BY rt.criado_em DESC
        LIMIT %s OFFSET %s
    """, (*params, limit, offset))
    tokens = cursor.fetchall()

    return jsonify({
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "total_results": total,
        "data": tokens
    }), 200

@plans_bp.route('/api/admin/token-blacklist', methods=['GET'])
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
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    offset = (page - 1) * limit

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, token, invalidado_em
        FROM token_blacklist
        ORDER BY invalidado_em DESC
        LIMIT %s OFFSET %s
    """, (limit, offset))
    tokens = cursor.fetchall()
    return jsonify(tokens), 200

@plans_bp.route('/api/admin/revoke-refresh-token', methods=['POST'])
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
    token = data.get("token")

    if not token:
        return jsonify({"error": "Token ausente!"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE refresh_tokens SET revogado = TRUE WHERE token = %s", (token,))
    conn.commit()

    return jsonify({"message": "Refresh token revogado com sucesso!"}), 200
