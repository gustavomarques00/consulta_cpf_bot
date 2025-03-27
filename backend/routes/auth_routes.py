from flask import Blueprint, request, jsonify
from utils.db import get_db_connection
from utils.token import generate_token, create_refresh_token
from utils.validators import is_valid_email, is_valid_password, is_valid_phone, valid_user_types
import bcrypt
import mysql.connector

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    telefone = data.get('telefone')
    tipo_usuario = data.get('tipoUsuario')
    senha = data.get('senha')
    confirmar_senha = data.get('confirmarSenha')
    cargo = data.get('cargo', 'Usuario')

    if not nome or not email or not telefone or not tipo_usuario or not senha or not confirmar_senha:
        return jsonify({"error": "Todos os campos são obrigatórios!"}), 400

    if senha != confirmar_senha:
        return jsonify({"error": "As senhas não coincidem!"}), 400

    if not is_valid_email(email):
        return jsonify({"error": "Email inválido!"}), 400

    if not is_valid_phone(telefone):
        return jsonify({"error": "Telefone inválido!"}), 400

    if not is_valid_password(senha):
        return jsonify({"error": "Senha fraca. Use uma mais segura!"}), 400

    if tipo_usuario not in valid_user_types:
        return jsonify({"error": f"Tipo de usuário inválido. Válidos: {', '.join(valid_user_types)}"}), 400

    hashed_senha = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"error": "Email já cadastrado!"}), 400

        cursor.execute(
            "INSERT INTO usuarios (nome, email, telefone, tipo_usuario, senha, cargo) VALUES (%s, %s, %s, %s, %s, %s)",
            (nome, email, telefone, tipo_usuario, hashed_senha, cargo)
        )
        conn.commit()
        return jsonify({"message": "Usuário registrado com sucesso!"}), 201

    except mysql.connector.Error as err:
        return jsonify({"error": f"Erro no banco de dados: {err}"}), 500
