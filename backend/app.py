from flask import Flask
from flask_cors import CORS
from routes.auth_routes import auth_bp
from dotenv import load_dotenv
import os
from routes.plans_routes import plans_bp
from flasgger import Swagger

app = Flask(__name__)
CORS(app)  # Permite CORS para a aplicação (acesso de diferentes domínios)

# Carregar variáveis do .env
load_dotenv()

# Acessar variáveis
JWT_SECRET = os.getenv('JWT_SECRET')
BASE_URL = os.getenv('BASE_URL')

# Configuração do Swagger
swagger_config = {
    "headers": [],
    "title": "API Planos JWT - Backend",
    "version": "1.0.0",
    "description": "Documentação da API de autenticação, planos e administração",
    "termsOfService": "",
    "static_url_path": "/flasgger_static",  # URL para os arquivos estáticos do Swagger
    "specs_route": "/apidocs/",  # Defina a URL onde o Swagger será acessado
    "swagger_ui": True,
    "specs": [
        {
            "endpoint": "swagger_api",  # Remova o ponto aqui para evitar o erro
            "route": "/swagger_api"     # Sem o ponto no endpoint
        }
    ]
}

swagger = Swagger(app, config=swagger_config)

# Registrar Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(plans_bp)

# Exibe as rotas no console
print(app.url_map)

if __name__ == '__main__':
    app.run(debug=True)  # Ativa o modo debug para facilitar o desenvolvimento
