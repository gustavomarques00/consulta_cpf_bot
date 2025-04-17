from flask import request, jsonify  # type: ignore
from functools import wraps
from services.auth_service import AuthService

auth_service = AuthService()


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token não fornecido ou malformado!"}), 401

        token = auth_header.split("Bearer ")[-1].strip()

        if not token:
            return jsonify({"error": "Token inválido ou ausente"}), 401

        if auth_service.is_token_blacklisted(token):
            return jsonify({"error": "Token revogado!"}), 401

        try:
            # Reutilizando o método decode_token do AuthService
            data = auth_service.decode_token(token)
            request.user_id = data.get("user_id")
            request.cargo = data.get("cargo")
        except ValueError as e:
            return jsonify({"error": str(e)}), 401

        return f(*args, **kwargs)

    return decorated


def only_super_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if getattr(request, "cargo", None) != "ADM":
            return (
                jsonify(
                    {
                        "error": "Acesso negado! Apenas Super Admins podem acessar esta rota."
                    }
                ),
                403,
            )
        return f(*args, **kwargs)

    return decorated


def permission_required(*required_permissions):
    """
    Middleware para verificar se o usuário autenticado possui uma ou mais permissões necessárias.
    :param required_permissions: Lista de permissões necessárias (ex.: "CHEFE DE EQUIPE", "ADM").
    """

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user_cargo = getattr(request, "cargo", None)

            # Verifica se o cargo está presente no token
            if not user_cargo:
                return (
                    jsonify({"error": "Cargo do usuário não encontrado no token"}),
                    403,
                )

            # Verifica se o cargo do usuário está entre as permissões necessárias
            if user_cargo not in required_permissions:
                return (
                    jsonify(
                        {
                            "error": f"Acesso negado! Permissões necessárias: {', '.join(required_permissions)}."
                        }
                    ),
                    403,
                )

            return f(*args, **kwargs)

        return decorated

    return decorator
