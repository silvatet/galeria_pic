import mysql.connector
import logging

# Configuração do logging
logging.basicConfig(filename="app.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Configurações do banco de dados
DB_HOST = '127.0.0.1'  # Endereço IP local
DB_USER = 'usuario'     # Substitua pelo seu nome de usuário
DB_PASSWORD = 'senha'   # Substitua pela sua senha
DB_DATABASE = 'teste'   # Substitua pelo nome do seu banco de dados


class ConnectionService:
    """Serviço para gerenciar conexões ao banco de dados."""

    @staticmethod
    def open_connection():
        """Abre a conexão com o banco de dados."""
        try:
            logging.info("Tentando abrir a conexão com o banco de dados.")
            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE
            )
            logging.info("Conexão aberta com sucesso.")
            return connection
        except mysql.connector.Error as err:
            logging.error(f"Erro ao conectar ao banco de dados: {err}")
            raise

    @staticmethod
    def close_connection(cursor=None, connection=None):
        """Fecha o cursor e a conexão do banco de dados."""
        try:
            if cursor:
                cursor.close()
                logging.info("Cursor fechado com sucesso.")
            if connection:
                connection.close()
                logging.info("Conexão fechada com sucesso.")
        except Exception as err:
            logging.error(f"Erro ao fechar a conexão ou cursor: {err}")
            raise


if __name__ == "__main__":
    """Testa a conexão com o banco de dados."""
    conn = None  # Inicializa a variável 'conn'
    try:
        conn = ConnectionService.open_connection()
        print("Conexão bem-sucedida!")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        # Verifica se a conexão foi realmente aberta antes de tentar fechá-la
        if conn:
            ConnectionService.close_connection(connection=conn)
        else:
            logging.error("Conexão não foi estabelecida, portanto não há o que fechar.")
