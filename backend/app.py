from flask import Flask, jsonify, request
import mysql.connector
import bcrypt
from flask_cors import CORS
import re
import os
import json
import jwt
import datetime
from dotenv import load_dotenv
from functools import wraps
import logging

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

# Configurar o logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Função para autenticar e ler dados do Google Sheets
def authenticate_google_sheets():
    """
    Autentica e retorna o serviço de API do Google Sheets.

    Essa função utiliza credenciais armazenadas em um arquivo de token para autenticar o acesso 
    ao Google Sheets e obtém um serviço de API autenticado.

    Returns:
        googleapiclient.discovery.Resource: Serviço autenticado para interagir com a API do Google Sheets.
    """
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
    """
    Lê os dados de uma planilha do Google Sheets e retorna uma lista de CPFs.

    Retorna uma lista de CPFs extraída de uma planilha especificada pelo ID e intervalo.

    Returns:
        list: Lista de CPFs lidos da planilha.
    """
    service = authenticate_google_sheets()
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])
    cpfs = [str(row[0]).strip().replace("\n", "").replace("\r", "") for row in values]
    return cpfs

# Função para validar CPF
def is_valid_cpf(cpf: str) -> bool:
    """
    Valida o CPF com base em sua formatação.

    A função remove caracteres especiais e verifica se o CPF contém 11 dígitos numéricos válidos.

    Parameters:
        cpf (str): O CPF a ser validado.

    Returns:
        bool: Retorna True se o CPF for válido, False caso contrário.
    """
    cpf = cpf.replace(".", "").replace("-", "")  # Remove caracteres especiais
    if len(cpf) != 11 or not cpf.isdigit():
        return False
    return True

# Função para validar o email
def is_valid_email(email):
    """
    Valida um endereço de e-mail usando uma expressão regular.

    A função verifica se o e-mail segue o padrão correto para endereços de e-mail.

    Parameters:
        email (str): O e-mail a ser validado.

    Returns:
        bool: Retorna True se o e-mail for válido, False caso contrário.
    """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

# Função para validar o telefone
def is_valid_phone(phone):
    """
    Valida um número de telefone com base no formato "(XX) XXXX-XXXX" ou "(XX) XXXXX-XXXX".

    A função utiliza uma expressão regular para garantir que o telefone esteja no formato correto.

    Parameters:
        phone (str): O número de telefone a ser validado.

    Returns:
        bool: Retorna True se o telefone for válido, False caso contrário.
    """
    phone_regex = r'^\(\d{2}\) \d{4,5}-\d{4}$'
    return re.match(phone_regex, phone) is not None

# Função para validar a senha
def is_valid_password(password):
    """
    Valida a senha de acordo com os critérios de segurança.

    A senha deve ter pelo menos 6 caracteres, incluindo uma letra maiúscula, um número e um caractere especial.

    Parameters:
        password (str): A senha a ser validada.

    Returns:
        bool: Retorna True se a senha for válida, False caso contrário.
    """
    return bool(re.match(r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$', password))

# Função para obter conexão com o banco de dados
def get_db_connection():
    """
    Estabelece uma conexão com o banco de dados MySQL.

    Retorna uma conexão com o banco de dados MySQL configurado com as credenciais no arquivo .env.

    Returns:
        mysql.connector.connection.MySQLConnection: A conexão com o banco de dados MySQL.
    """
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4'  # Definir a codificação como utf8mb4 para suportar emojis
    )

# Função para criar um refresh token
def create_refresh_token(user_id):
    """
    Cria um refresh token para o usuário.

    O refresh token é usado para renovar o JWT do usuário quando ele expira.

    Parameters:
        user_id (int): O ID do usuário para o qual o refresh token será gerado.

    Returns:
        str: O refresh token gerado.
    """
    return jwt.encode(
        {"user_id": user_id, "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30)},  # Expira em 30 dias
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )

# Função para decodificar e validar o token JWT
def decode_and_validate_token(token):
    """
    Decodifica e valida um token JWT, verificando a expiração e a assinatura.
    Verifica se o cargo do usuário é 'ADM'.

    Parameters:
        token (str): O token JWT a ser decodificado e validado.

    Returns:
        dict: Dados do token decodificado ou erro se o token for inválido ou expirado.
    """
    try:
        # Decodificar o token com a chave secreta
        data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        # Verificar a data de expiração
        expiration_date = datetime.datetime.utcfromtimestamp(data['exp'])
        if expiration_date < datetime.datetime.utcnow():
            return {"error": "Token expirado!"}

        # Verificar o cargo do usuário
        if data.get("cargo") != "ADM":
            return {"error": "Acesso negado! Cargo necessário: ADM."}

        return data  # Retorna os dados decodificados do token

    except jwt.ExpiredSignatureError:
        return {"error": "Token expirado!"}
    except jwt.InvalidTokenError:
        return {"error": "Token inválido!"}

# Função para gerar um novo token de acesso
def generate_token(user_id, cargo, expiration_years=5):
    """
    Gera um token de acesso para o usuário com cargo 'ADM', com validade configurada para 5 anos.

    Parameters:
        user_id (int): O ID do usuário.
        cargo (str): O cargo do usuário.
        expiration_years (int): O número de anos que o token será válido (default 5 anos).

    Returns:
        str: O token JWT gerado.
    """
    # Calculando a data de expiração do token (5 anos)
    expiration_date = datetime.datetime.utcnow() + datetime.timedelta(days=365*expiration_years)

    # Payload do token com as informações do usuário
    payload = {
        "user_id": user_id,
        "cargo": cargo,  # O cargo do usuário
        "exp": expiration_date  # Expiração do token
    }

    # Gerando o token
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token

@app.route('/api/user-plans', methods=['GET'])
def get_user_plan():
    """
    Rota para retornar o plano atual de um usuário.

    Este endpoint verifica o token do usuário e retorna os detalhes do plano atual associado ao usuário.
    Se o token estiver ausente ou inválido, ou se o plano não for encontrado, uma mensagem de erro será retornada.

    Returns:
        json: Detalhes do plano do usuário ou erro.
    """
    # Obter o token de autorização dos headers
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Token de autenticação ausente!"}), 401

    try:
        # Decodificar o token e obter o ID do usuário
        data = jwt.decode(token.split(" ")[1], JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = data['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado!"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido!"}), 401

    # Consultar o banco de dados para obter o plano associado ao usuário
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT p.id, p.nome, p.preco, p.features FROM usuarios_planos up "
                   "JOIN planos p ON up.plano_id = p.id WHERE up.usuario_id = %s", (user_id,))
    user_plan = cursor.fetchone()
    conn.close()

    if not user_plan:
        return jsonify({"error": "Plano não encontrado para este usuário!"}), 404

    return jsonify(user_plan), 200

# Rota para renovar o token
@app.route('/api/refresh-token', methods=['POST'])
def refresh_token():
    """
    Rota para renovar o token de autenticação usando um refresh token.

    O refresh token é enviado nos headers da requisição, e a função retorna um novo JWT.

    Returns:
        json: Um novo JWT, ou mensagem de erro caso o refresh token seja inválido ou expirado.
    """
    refresh_token = request.headers.get('Refresh-Token')
    if not refresh_token:
        return jsonify({"error": "Refresh token ausente!"}), 401

    try:
        data = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = data['user_id']
        new_token = jwt.encode(
            {"user_id": user_id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)},  # Novo JWT com 1 hora de validade
            JWT_SECRET,
            algorithm=JWT_ALGORITHM
        )
        return jsonify({"token": new_token}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Refresh token expirado!"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Refresh token inválido!"}), 401

# Rota para registrar um novo usuário
@app.route('/register', methods=['POST'])
def register():
    """
    Rota para registrar um novo usuário no sistema.

    Requer:
        nome (str): Nome completo do usuário.
        email (str): Email do usuário.
        telefone (str): Telefone do usuário (formato: (XX) XXXX-XXXX).
        tipoUsuario (str): Tipo de usuário (Operador, Chefe de Equipe, Independente, ADM).
        senha (str): Senha do usuário.
        confirmarSenha (str): Confirmação da senha.

    Retorna:
        json: Resposta JSON com sucesso ou erro.
    """
    data = request.get_json()

    nome = data.get('nome')
    email = data.get('email')
    telefone = data.get('telefone')
    tipo_usuario = data.get('tipoUsuario')  
    senha = data.get('senha')
    confirmar_senha = data.get('confirmarSenha')
    cargo = data.get('cargo', 'Usuario')  # Se não for passado, o cargo padrão será 'Usuario'

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
                "INSERT INTO usuarios (nome, email, telefone, tipo_usuario, senha, cargo) VALUES (%s, %s, %s, %s, %s, %s)",
                (nome, email, telefone, tipo_usuario, hashed_senha, cargo)
            )
            conn.commit()

    except mysql.connector.Error as err:
        return jsonify({"error": f"Erro no banco de dados: {err}"}), 500

    return jsonify({"message": "Usuário registrado com sucesso!"}), 201

if __name__ == '__main__':
    app.run(debug=True)
