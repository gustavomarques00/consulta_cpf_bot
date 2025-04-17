import jwt  # type: ignore
import datetime
import logging
from backend.core.db import get_db_connection
from core.config import Config
from services.token_service import TokenService
import bcrypt  # type: ignore
from utils.validators import VALID_USER_TYPES, is_valid_email, is_valid_password, is_valid_phone  # type: ignore

# Configuração de logs
logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self):
        self.jwt_secret = Config.JWT_SECRET
        self.jwt_algorithm = Config.JWT_ALGORITHM

    def decode_token(self, token):
        """
        Decodifica um token JWT.
        """
        try:
            return jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
        except jwt.ExpiredSignatureError:
            logger.warning("Tentativa de uso de token expirado.")
            raise ValueError("Token expirado!")
        except jwt.InvalidTokenError:
            logger.warning("Tentativa de uso de token inválido.")
            raise ValueError("Token inválido!")

    def is_token_blacklisted(self, token):
        """
        Verifica se o token está na blacklist.
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM token_blacklist WHERE token = %s", (token,))
            is_blacklisted = cursor.fetchone() is not None
            if is_blacklisted:
                logger.info(f"Token revogado detectado: {token}")
            return is_blacklisted
        except Exception as e:
            logger.error(f"Erro ao verificar blacklist: {e}")
            raise ValueError("Erro ao verificar blacklist.")
        finally:
            conn.close()

    def generate_and_store_access_token(self, user_id, cargo, plano_nome="Free"):
        """
        Gera e retorna um token de acesso.
        """
        access_token = TokenService.generate_access_token(user_id, cargo)
        expira_em = datetime.datetime.now() + datetime.timedelta(hours=2)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Busca o ID do plano pelo nome
            cursor.execute("SELECT id FROM planos WHERE planos = %s", (plano_nome,))
            plano = cursor.fetchone()
            if not plano:
                raise ValueError(
                    f"Plano '{plano_nome}' não encontrado no banco de dados."
                )

            plano_id = plano[0]

            # Insere o token na tabela
            cursor.execute(
                """
                INSERT INTO tokens (usuario_id, token, criado_em, expira_em, plano_id)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    access_token,
                    datetime.datetime.now(),
                    expira_em,
                    plano_id,
                ),
            )
            conn.commit()
            logger.info(
                f"Token gerado e armazenado para o usuário {user_id} com plano ID {plano_id}."
            )
        except Exception as e:
            logger.error(f"Erro ao salvar token no banco: {e}")
            raise ValueError(f"Erro ao salvar token no banco: {e}")
        finally:
            cursor.close()
            conn.close()

        return access_token

    def revoke_token(self, token):
        """
        Revoga um token adicionando-o à blacklist.
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO token_blacklist (token, invalidado_em)
                VALUES (%s, %s)
                """,
                (token, datetime.datetime.now()),
            )
            conn.commit()
            logger.info(f"Token revogado com sucesso: {token}")
        except Exception as e:
            logger.error(f"Erro ao revogar token: {e}")
            raise ValueError(f"Erro ao revogar token: {e}")
        finally:
            cursor.close()
            conn.close()
            logger.info("Conexão com o banco fechada")

    def register_user(self, nome, email, telefone, cargo, senha):
        """
        Registra um novo usuário no banco de dados.

        Args:
            nome (str): Nome do usuário.
            email (str): Email do usuário.
            telefone (str): Telefone do usuário.
            cargo (str): Cargo do usuário.
            senha (str): Senha do usuário (será criptografada).

        Raises:
            ValueError: Se o email já estiver cadastrado ou ocorrer um erro de validação.
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Verifica se o email já está cadastrado
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone():
                raise ValueError("Email já cadastrado!")

            # Criptografa a senha
            hashed_password = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())

            # Insere o novo usuário no banco de dados
            cursor.execute(
                """
                INSERT INTO usuarios (nome, email, telefone, cargo, senha)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (nome, email, telefone, cargo, hashed_password),
            )
            conn.commit()
            logger.info(f"Usuário {nome} registrado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao registrar usuário: {e}")
            raise ValueError(f"Erro ao registrar usuário: {e}")
        finally:
            cursor.close()
            conn.close()

    def validate_user_data(self, email, telefone, senha, confirmar_senha, cargo):
        """
        Valida os dados do usuário antes do registro.

        Args:
            email (str): Email do usuário.
            telefone (str): Telefone do usuário.
            senha (str): Senha do usuário.
            confirmar_senha (str): Confirmação da senha.
            cargo (str): Cargo do usuário.

        Returns:
            tuple: (mensagem de erro, código HTTP) em caso de erro, ou None se os dados forem válidos.
        """
        # Verificação de confirmação da senha
        if senha != confirmar_senha:
            return {"error": "As senhas não coincidem!"}, 400

        # Validação do email
        if not is_valid_email(email):
            return {"error": "Email inválido!"}, 400

        # Validação do telefone
        if not is_valid_phone(telefone):
            return {"error": "Telefone inválido! Use o formato (XX) XXXXX-XXXX."}, 400

        # Validação da senha
        if not is_valid_password(senha):
            return {"error": "Senha fraca. Use uma mais segura!"}, 400

        # Validação do cargo
        if cargo not in VALID_USER_TYPES:
            return {
                "error": f"Cargo inválido! Cargos permitidos: {', '.join(VALID_USER_TYPES)}."
            }, 400

        # Dados válidos
        return None
