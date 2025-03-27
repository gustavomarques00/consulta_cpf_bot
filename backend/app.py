from flask import Flask
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.plans_routes import plans_bp

app = Flask(__name__)
CORS(app)

# Registrar blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(plans_bp)
print(app.url_map)


if __name__ == '__main__':
    app.run(debug=True)
