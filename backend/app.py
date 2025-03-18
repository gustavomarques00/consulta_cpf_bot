from flask import Flask, jsonify, request
import mysql.connector
import bcrypt
import re
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

# Carregar as credenciais do banco de dados do arquivo .env
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'sua_aplicacao')

# Função para validar o email
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

# Função para validar o telefone
def is_valid_phone(phone):
    phone_regex = r'^\(\d{2}\) \d{4,5}-\d{4}$'
    return re.match(phone_regex, phone) is not None

# Função para validar a senha
def is_valid_password(password):
    return bool(re.match(r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$', password))

# Lista de tipos de usuário válidos
valid_user_types = ["Operador", "Chefe de Equipe", "Independente"]

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    nome = data.get('nome')
    email = data.get('email')
    telefone = data.get('telefone')
    tipo_usuario = data.get('tipoUsuario')  # Alteração para tipo de usuário
    senha = data.get('senha')
    confirmar_senha = data.get('confirmarSenha')

    # Validação de campos obrigatórios
    if not nome or not email or not telefone or not tipo_usuario or not senha or not confirmar_senha:
        return jsonify({"error": "Todos os campos são obrigatórios!"}), 400

    # Validar se as senhas coincidem
    if senha != confirmar_senha:
        return jsonify({"error": "As senhas não coincidem!"}), 400

    # Validar formato de email
    if not is_valid_email(email):
        return jsonify({"error": "Email inválido!"}), 400

    # Validar formato de telefone
    if not is_valid_phone(telefone):
        return jsonify({"error": "Telefone inválido! Use o formato (XX) XXXX-XXXX ou (XX) XXXXX-XXXX"}), 400

    # Validar a senha (complexidade mínima)
    if not is_valid_password(senha):
        return jsonify({"error": "A senha deve ter pelo menos 6 caracteres, incluindo uma letra maiúscula, um número e um caractere especial!"}), 400

    # Validar tipo de usuário
    if tipo_usuario not in valid_user_types:
        return jsonify({"error": f"Tipo de usuário inválido! Os tipos válidos são: {', '.join(valid_user_types)}"}), 400

    # Criptografar a senha
    hashed_senha = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

    try:
        # Conectar ao banco de dados MySQL
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        # Usando o cursor com o contexto 'with' para garantir o fechamento correto
        with conn.cursor() as cursor:
            # Verificar se o email já existe
            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({"error": "Email já cadastrado!"}), 400

            # Inserir os dados no banco de dados
            cursor.execute(
                "INSERT INTO usuarios (nome, email, telefone, tipo_usuario, senha) VALUES (%s, %s, %s, %s, %s)",
                (nome, email, telefone, tipo_usuario, hashed_senha)
            )
            conn.commit()

    except mysql.connector.Error as err:
        return jsonify({"error": f"Erro no banco de dados: {err}"}), 500

    return jsonify({"message": "Usuário registrado com sucesso!"}), 201

if __name__ == '__main__':
    app.run(debug=True)
