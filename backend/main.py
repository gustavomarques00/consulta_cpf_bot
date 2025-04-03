from flask import Flask, jsonify  # type: ignore
from flask_cors import CORS  # type: ignore
from flasgger import Swagger  # type: ignore
import logging

from backend.core.config import Config  # ✅ Variáveis centralizadas
from routes.auth_routes import auth_bp  # 🔐 Autenticação
from routes.plans_routes import plans_bp  # 📦 Planos
from routes.brsmm_routes import brsmm_bp  # 🔗 BRSMM
from routes.trafego_routes import trafego_bp  # 🚦 Tráfego diário


# =============================
# 🚀 Inicialização do Flask
# =============================
app = Flask(__name__)
CORS(app)

# =============================
# 📄 Configuração Swagger
# =============================
swagger_config = {
    "headers": [],
    "title": "API Planos JWT - Backend",
    "version": "1.0.0",
    "description": "Documentação da API de autenticação, planos e tráfego",
    "termsOfService": "",
    "static_url_path": "/flasgger_static",
    "specs_route": "/apidocs/",
    "swagger_ui": True,
    "uiversion": 3,
    "specs": [
        {
            "endpoint": "swagger_api",
            "route": "/swagger_api",
        }
    ],
}
swagger = Swagger(app, config=swagger_config)


# 🔧 Endpoint da especificação JSON para o Swagger UI
@app.route("/swagger_api")
def swagger_api():
    return jsonify(swagger.template)

# =============================
# 📜 Configuração de Log
# =============================

logging.basicConfig(
    level=logging.DEBUG,  # Gravar todos os tipos de logs (DEBUG, INFO, WARNING, ERROR)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/geral.log"),  # Log em arquivo
        logging.StreamHandler(),  # Log no console
    ]
)


# =============================
# 🔗 Registro de Blueprints
# =============================
app.register_blueprint(auth_bp)
app.register_blueprint(plans_bp)
app.register_blueprint(brsmm_bp)
app.register_blueprint(trafego_bp)

# =============================
# 🔐 Log de Configuração
# =============================
#print(f"🔐 JWT_SECRET: {Config.JWT_SECRET}")
#print(f"🌐 BASE_URL: {Config.BASE_URL}")
#print("📡 Rotas disponíveis:")
#print(app.url_map)

# =============================
# 🏁 Inicialização
# =============================
if __name__ == "__main__":
    app.run(debug=True)
