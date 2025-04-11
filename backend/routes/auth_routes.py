import logging
import bcrypt  # type: ignore
import mysql.connector
from flask import Blueprint, request, jsonify  # type: ignore
from core.db import get_db_connection
from utils.validators import (
    insert_user,
    is_email_registered,
    validate_user_data,
)
from flasgger.utils import swag_from  # type: ignore

# Configuração do Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint de autenticação
auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")

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
                        "confirmarSenha": {
                            "type": "string",
                            "example": "SenhaForte123!",
                        },
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
                            "example": "Usuário registrado com sucesso!",
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
                            "example": "Erro no banco de dados: ...",
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

    # Extrair dados do corpo da requisição
    required_fields = ["nome", "email", "telefone", "cargo", "senha", "confirmarSenha"]
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        logger.warning(f"Campos obrigatórios ausentes: {', '.join(missing_fields)}")
        return jsonify({"error": f"Campos obrigatórios: {', '.join(missing_fields)}"}), 400

    nome = data["nome"]
    email = data["email"]
    telefone = data["telefone"]
    cargo = data["cargo"]
    senha = data["senha"]
    confirmar_senha = data["confirmarSenha"]

    # Validações
    validation_error = validate_user_data(email, telefone, senha, confirmar_senha, cargo)
    if validation_error:
        return validation_error

    # Verifica se o cargo é válido
    cargos_validos = ["ADM", "OPERADOR", "CHEFE DE EQUIPE"]
    if cargo not in cargos_validos:
        logger.warning(f"Cargo inválido: {cargo}")
        return jsonify({"error": f"Cargo inválido. Os cargos válidos são: {', '.join(cargos_validos)}"}), 400

    # Criptografar a senha
    hashed_senha = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())
    logger.info(f"Senha criptografada para o usuário {nome}.")

    # Inserir no banco de dados
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifica se o email já está cadastrado
        if is_email_registered(cursor, email):
            logger.warning(f"Email já cadastrado: {email}")
            return jsonify({"error": "Email já cadastrado!"}), 400

        # Insere o novo usuário
        insert_user(cursor, nome, email, telefone, cargo, hashed_senha)
        conn.commit()
        logger.info(f"Usuário {nome} registrado com sucesso.")

        return jsonify({"message": "Usuário registrado com sucesso!"}), 201

    except mysql.connector.Error as err:
        logger.error(f"Erro no banco de dados: {err}")
        return jsonify({"error": f"Erro no banco de dados: {err}"}), 500
    finally:
        if conn:
            conn.close()