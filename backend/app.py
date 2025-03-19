from flask import Flask, jsonify, request
import mysql.connector
import bcrypt
from flask_cors import CORS
import re
import os
import openpyxl
import json
import jwt
import datetime
from dotenv import load_dotenv
from functools import wraps
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)
CORS(app)  # Isso permitirá requisições de qualquer origem

# Carregar as credenciais do banco de dados do arquivo .env
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'sua_aplicacao')

# Carregar JWT Secret e outras configurações do arquivo .env
JWT_SECRET = os.getenv('JWT_SECRET', 'secretdoapp')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_EXPIRES = int(os.getenv('JWT_EXPIRES', 36000))  # Definir tempo de expiração (em segundos)

# Função para autenticar e ler dados do Google Sheets
def authenticate_google_sheets():
    creds = None
    if os.path.exists('token.json'):
        creds, project = google.auth.load_credentials_from_file('token.json')
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credenciais.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('sheets', 'v4', credentials=creds)

# Função para ler dados de uma planilha do Google Sheets
def read_google_sheet():
    service = authenticate_google_sheets()
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])
    cpfs = [str(row[0]).strip().replace("\n", "").replace("\r", "") for row in values]
    return cpfs

# Função para validar CPF
def is_valid_cpf(cpf: str) -> bool:
    cpf = cpf.replace(".", "").replace("-", "")  # Remove caracteres especiais
    if len(cpf) != 11 or not cpf.isdigit():
        return False
    # Lógica adicional de validação pode ser inserida aqui
    return True

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

# Função para obter conexão com o banco de dados
def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4'  # Definir a codificação como utf8mb4 para suportar emojis
    )

# Função para calcular o preço final do plano baseado no custo do bot e na margem
def calculate_final_price(custo_bot, margem):
    return round(custo_bot + margem, 2)  # Preço final como a soma do custo e da margem

# Rota para retornar todos os planos
@app.route('/api/plans', methods=['GET'])
def get_plans():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nome, custo_bot, margem, preco_final, features FROM planos")
    plans = cursor.fetchall()
    conn.close()

    # Processar os benefícios para garantir que seja um array válido
    for plan in plans:
        # Verificar se 'features' é um string JSON e convertê-lo para uma lista
        if isinstance(plan['features'], str):
            plan['features'] = json.loads(plan['features'])
        elif not isinstance(plan['features'], list):
            plan['features'] = []  # Caso não seja nem string nem lista, definimos como array vazio

        plan['preco_final'] = calculate_final_price(plan['custo_bot'], plan['margem'])

    return jsonify(plans), 200


# Rota para retornar o plano atual do usuário
@app.route('/api/user-plans', methods=['GET'])
def get_user_plan():
    # Simula o plano atual do usuário
    user_plan = {
        "name": "Plano Pro",
        "renewalDate": "2025-03-15"
    }
    return jsonify(user_plan), 200

# Middleware de autenticação
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # A parte do token após 'Bearer'

        if not token:
            return jsonify({"error": "Token de autenticação ausente!"}), 401

        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido!"}), 401

        return f(current_user_id, *args, **kwargs)

    return decorated_function

# Rota para registrar um novo usuário
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    nome = data.get('nome')
    email = data.get('email')
    telefone = data.get('telefone')
    tipo_usuario = data.get('tipoUsuario')  
    senha = data.get('senha')
    confirmar_senha = data.get('confirmarSenha')

    if not nome or not email or not telefone or not tipo_usuario or not senha or not confirmar_senha:
        return jsonify({"error": "Todos os campos são obrigatórios!"}), 400

    if senha != confirmar_senha:
        return jsonify({"error": "As senhas não coincidem!"}), 400

    if not is_valid_email(email):
        return jsonify({"error": "Email inválido!"}), 400

    if not is_valid_phone(telefone):
        return jsonify({"error": "Telefone inválido!"}), 400

    if not is_valid_password(senha):
        return jsonify({"error": "A senha deve ter pelo menos 6 caracteres, incluindo uma letra maiúscula, um número e um caractere especial!"}), 400

    if tipo_usuario not in valid_user_types:
        return jsonify({"error": f"Tipo de usuário inválido! Os tipos válidos são: {', '.join(valid_user_types)}"}), 400

    hashed_senha = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({"error": "Email já cadastrado!"}), 400

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
