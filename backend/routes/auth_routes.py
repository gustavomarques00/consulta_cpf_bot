import os
import logging
import bcrypt  # type: ignore
import mysql.connector
from flask import Blueprint, request, jsonify  # type: ignore
from core.db import get_db_connection
from utils.validators import (
    is_valid_email,
    is_valid_password,
    is_valid_phone,
    valid_user_types,
)
from flasgger.utils import swag_from  # type: ignore

# Configuração do Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint de autenticação
auth_bp = Blueprint("auth_bp", __name__)


import os
import logging
import bcrypt  # type: ignore
import mysql.connector
from flask import Blueprint, request, jsonify  # type: ignore
from core.db import get_db_connection
from utils.validators import (
    is_valid_email,
    is_valid_password,
    is_valid_phone,
)
from flasgger.utils import swag_from  # type: ignore

# Configuração do Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint de autenticação
auth_bp = Blueprint("auth_bp", __name__)

valid_user_types = ["ADM", "CHEFE DE EQUIPE", "OPERADOR"]  # Cargos válidos

@auth_bp.route("/register", methods=["POST"])
@swag_from(
    {
        "tags": ["Autenticação"],
        "summary": "Cria um novo usuário",
        "description": "Endpoint para cadastro de um novo usuário, com validações e senha criptografada.",
        "consumes": ["application/json"],
        "parameters": [
            {
                "name": "body",
                "in": "body",
                "description": "Dados do novo usuário",
                "required": True,
                "schema": {
                    "type": "object",
                    "required": [
                        "nome",
                        "email",
                        "telefone",
                        "cargo",
                        "senha",
                        "confirmarSenha",
                    ],
                    "properties": {
                        "nome": {"type": "string", "example": "Gustavo Marques"},
                        "email": {"type": "string", "example": "gustavo@email.com"},
                        "telefone": {"type": "string", "example": "(11) 91234-5678"},
                        "cargo": {"type": "string", "example": "ADM"},
                        "senha": {"type": "string", "example": "SenhaForte123!"},
                        "confirmarSenha": {"type": "string", "example": "SenhaForte123!"},
                    },
                },
            }
        ],
        "responses": {
            201: {
                "description": "Usuário registrado com sucesso",
                "schema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "example": "Usuário registrado com sucesso!"
                        }
                    },
                },
            },
            400: {
                "description": "Erro de validação nos dados de entrada",
                "schema": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "example": "Email já cadastrado!"}
                    },
                },
            },
            500: {
                "description": "Erro interno do servidor ou banco de dados",
                "schema": {
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "string",
                            "example": "Erro no banco de dados: ..."
                        }
                    },
                },
            },
        },
    }
)
def register():
    logger.info("Iniciando o cadastro de um novo usuário.")
    data = request.get_json()

    nome = data.get("nome")
    email = data.get("email")
    telefone = data.get("telefone")
    cargo = data.get("cargo")
    senha = data.get("senha")
    confirmar_senha = data.get("confirmarSenha")

    # ===== Validações dos dados recebidos =====
    if not nome or not email or not telefone or not cargo or not senha or not confirmar_senha:
        logger.warning("Todos os campos são obrigatórios!")
        return jsonify({"error": "Todos os campos são obrigatórios!"}), 400

    if senha != confirmar_senha:
        logger.warning("As senhas não coincidem!")
        return jsonify({"error": "As senhas não coincidem!"}), 400

    if not is_valid_email(email):
        logger.warning(f"Email inválido: {email}")
        return jsonify({"error": "Email inválido!"}), 400

    if not is_valid_phone(telefone):
        logger.warning(f"Telefone inválido: {telefone}")
        return jsonify({"error": "Telefone inválido!"}), 400

    if not is_valid_password(senha):
        logger.warning("Senha fraca.")
        return jsonify({"error": "Senha fraca. Use uma mais segura!"}), 400

    if cargo not in valid_user_types:
        logger.warning(f"Cargo inválido: {cargo}")
        return jsonify({"error": f"Cargo inválido. Válidos: {', '.join(valid_user_types)}"}), 400

    # Criptografar a senha com bcrypt
    hashed_senha = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())
    logger.info(f"Senha criptografada para o usuário {nome}.")

    # ===== Inserção no banco de dados =====
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifica se o email já está cadastrado
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            logger.warning(f"Email já cadastrado: {email}")
            return jsonify({"error": "Email já cadastrado!"}), 400

        # Insere o novo usuário
        cursor.execute(
            """
            INSERT INTO usuarios (nome, email, telefone, cargo, senha)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (nome, email, telefone, cargo, hashed_senha),
        )
        conn.commit()
        logger.info(f"Usuário {nome} registrado com sucesso.")

        return jsonify({"message": "Usuário registrado com sucesso!"}), 201

    except mysql.connector.Error as err:
        logger.error(f"Erro no banco de dados: {err}")
        return jsonify({"error": f"Erro no banco de dados: {err}"}), 500
    finally:
        if conn:
            conn.close()
