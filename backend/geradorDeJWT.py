import jwt
import datetime
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Carregar a chave secreta do arquivo .env
JWT_SECRET = os.getenv('JWT_SECRET', 'secretdoapp')

# Gerar um token JWT manualmente
def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=10)  # Usa o UTC com timezone-aware
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    return token

# Gerar um token para um usuário com user_id = 1 (ou qualquer outro id que você queira)
token = generate_token(1)
print(f"Seu token JWT gerado é: {token}")
print("Use este token para autenticar suas requisições!")