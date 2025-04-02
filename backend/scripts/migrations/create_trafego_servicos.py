import mysql.connector
from core.config import Config


def criar_tabela_trafego_servicos():
    conn = mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
    )
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS trafego_servicos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            brsmm_id INT NOT NULL,
            nome VARCHAR(100),
            categoria VARCHAR(100),
            tipo VARCHAR(100),
            preco_base FLOAT,
            markup_percent FLOAT DEFAULT 50.0,
            disponivel BOOLEAN DEFAULT TRUE
        );
    """
    )

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Tabela 'trafego_servicos' criada com sucesso!")


if __name__ == "__main__":
    criar_tabela_trafego_servicos()
