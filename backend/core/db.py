import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from backend.core.config import Config  # usa as envs centralizadas

load_dotenv()


def get_db_connection():
    """
    Cria e retorna uma conexão com o banco de dados MySQL.

    :return: conexão ativa com o banco
    :rtype: mysql.connector.connection.MySQLConnection
    :raises: Exception se falhar ao conectar
    """
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            charset="utf8mb4",
        )

        if connection.is_connected():
            return connection
        else:
            raise Exception("❌ Não foi possível conectar ao banco de dados.")

    except Error as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        raise
