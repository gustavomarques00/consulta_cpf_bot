import os
import csv
from flask import Blueprint, jsonify, request, send_file
from datetime import datetime
from io import StringIO
from flasgger import swag_from
from backend.core.config import Config
from middlewares.auth_middleware import token_required

trafego_bp = Blueprint("trafego", __name__, url_prefix="/api/trafego")


@trafego_bp.route("/historico", methods=["GET"])
@token_required
@swag_from({
    'tags': ['Tráfego'],
    'summary': 'Consultar histórico de envios de tráfego',
    'parameters': [
        {'name': 'data', 'in': 'query', 'description': 'Data no formato YYYY-MM-DD', 'schema': {'type': 'string'}},
        {'name': 'status', 'in': 'query', 'description': 'Filtro por status: sucesso ou erro', 'schema': {'type': 'string'}}
    ],
    'responses': {
        200: {'description': 'Histórico retornado com sucesso'},
        404: {'description': 'Log não encontrado'}
    }
})
def consultar_historico():
    data_param = request.args.get("data")
    status_param = request.args.get("status")
    log_dir = os.path.join(Config.BASE_DIR, "logs", "brsmm")

    if not os.path.exists(log_dir):
        return jsonify({"message": "Nenhum log disponível ainda."}), 200

    if data_param:
        log_path = os.path.join(log_dir, f"brsmm_{data_param}.log")
        if not os.path.exists(log_path):
            return jsonify({"error": "Log não encontrado para a data informada"}), 404

        with open(log_path, "r", encoding="utf-8") as f:
            linhas = [l.strip() for l in f.readlines()]

        if status_param:
            status_param = status_param.lower()
            if status_param == "sucesso":
                linhas = [l for l in linhas if "✅" in l]
            elif status_param == "erro":
                linhas = [l for l in linhas if "❌" in l or "💥" in l]

        return jsonify({"data": linhas})

    # Lista completa
    historico = {}
    for nome in sorted(os.listdir(log_dir), reverse=True):
        if nome.startswith("brsmm_") and nome.endswith(".log"):
            data_log = nome.replace("brsmm_", "").replace(".log", "")
            with open(os.path.join(log_dir, nome), "r", encoding="utf-8") as f:
                linhas = [l.strip() for l in f.readlines()]
                if status_param:
                    if status_param == "sucesso":
                        linhas = [l for l in linhas if "✅" in l]
                    elif status_param == "erro":
                        linhas = [l for l in linhas if "❌" in l or "💥" in l]
                historico[data_log] = linhas

    return jsonify(historico)


@trafego_bp.route("/exportar", methods=["GET"])
@token_required
@swag_from({
    'tags': ['Tráfego'],
    'summary': 'Exportar log diário para CSV',
    'parameters': [
        {'name': 'data', 'in': 'query', 'required': True, 'description': 'Data no formato YYYY-MM-DD'}
    ],
    'responses': {
        200: {'description': 'Arquivo CSV gerado com sucesso'},
        404: {'description': 'Log não encontrado'}
    }
})
def exportar_csv():
    data_param = request.args.get("data")
    if not data_param:
        return jsonify({"error": "Parâmetro 'data' é obrigatório (YYYY-MM-DD)"}), 400

    log_path = os.path.join(Config.BASE_DIR, "logs", "brsmm", f"brsmm_{data_param}.log")
    if not os.path.exists(log_path):
        return jsonify({"error": "Log não encontrado"}), 404

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Linha"])  # Cabeçalho

    with open(log_path, "r", encoding="utf-8") as file:
        for linha in file:
            writer.writerow([linha.strip()])

    output.seek(0)
    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"trafego_{data_param}.csv"
    )

@trafego_bp.route("/send", methods=["POST"])
@token_required
@swag_from({
    'tags': ['Tráfego'],
    'summary': 'Enviar tráfego manualmente para uma URL',
    'requestBody': {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "service_id": {"type": "integer"},
                        "url": {"type": "string"},
                        "quantidade": {"type": "integer"}
                    },
                    "required": ["service_id", "url", "quantidade"]
                }
            }
        }
    },
    'responses': {
        200: {'description': 'Tráfego enviado com sucesso'},
        400: {'description': 'Erro de validação ou requisição'}
    }
})
def enviar_trafego_manual():
    from services.brsmm_service import BrsmmService

    data = request.get_json()
    service_id = data.get("service_id")
    url = data.get("url")
    quantidade = data.get("quantidade")

    if not all([service_id, url, quantidade]):
        return jsonify({"error": "Campos obrigatórios: service_id, url, quantidade"}), 400

    api = BrsmmService()
    response = api.add_order(link=url, service_id=service_id, quantity=quantidade)

    if "order" in response:
        return jsonify({"message": "✅ Pedido enviado com sucesso", "order_id": response["order"]}), 200
    else:
        return jsonify({"error": response}), 400

