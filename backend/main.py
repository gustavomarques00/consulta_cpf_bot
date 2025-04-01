from flask import Flask
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.plans_routes import plans_bp
from backend.core.config import Config  # ✅ Puxando variáveis do Config
from flasgger import Swagger
import os

# =============================
# 🚀 Inicialização do Flask
# =============================
app = Flask(__name__)
CORS(app)

# =============================
# 📄 Swagger
# =============================
swagger_config = {
    "headers": [],
    "title": "API Planos JWT - Backend",
    "version": "1.0.0",
    "description": "Documentação da API de autenticação, planos e administração",
    "termsOfService": "",
    "static_url_path": "/flasgger_static",
    "specs_route": "/apidocs/",
    "swagger_ui": True,
    "specs": [{"endpoint": "swagger_api", "route": "/swagger_api"}],
}

swagger = Swagger(app, config=swagger_config)

# =============================
# 🔗 Blueprints
# =============================
app.register_blueprint(auth_bp)
app.register_blueprint(plans_bp)

# =============================
# 🔐 Configurações Visuais (Opcional)
# =============================
print(f"🔐 JWT_SECRET: {Config.JWT_SECRET}")
print(f"🌐 BASE_URL: {Config.BASE_URL}")
print("📡 Rotas disponíveis:")
print(app.url_map)

# =============================
# 🏁 Inicialização do servidor
# =============================
if __name__ == "__main__":
    app.run(debug=True)
