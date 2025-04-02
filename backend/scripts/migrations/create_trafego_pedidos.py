import mysql.connector
from core.config import Config


def criar_tabela_trafego_pedidos():
    conn = mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
    )
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE trafego_pedidos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT NOT NULL,
            pedido_id_brsmm INT,
            service_id INT,
            url TEXT,
            quantidade INT,
            preco_unitario DECIMAL(10,4),
            preco_total DECIMAL(10,4),
            status VARCHAR(50) DEFAULT 'Pendente',
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,

            INDEX idx_usuario_id (usuario_id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );
    """
    )

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Tabela 'trafego_pedidos' criada com sucesso!")


if __name__ == "__main__":
    criar_tabela_trafego_pedidos()
