import logging
from mysql.connector import Error

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class Hostinger:
    @staticmethod
    def fetch_data(cursor):
        """
        Recupera os IDs das imagens que atendem aos critérios do banco de dados.

        Critérios:
        - `a.IsSent = 1`: Autenticação foi enviada.
        - `p.IsImpressed = 1`: Imagem foi marcada como "impressionada".

        As imagens são ordenadas em ordem decrescente pelo ID.

        :param cursor: Cursor ativo do banco de dados.
        :return: Lista de IDs das imagens.
        """
        try:
            logging.info("Iniciando a recuperação de IDs de imagens do banco de dados...")
            sql = """
                SELECT p.ImageId
                FROM Portfolio p
                JOIN Authentication a ON a.AuthenticationId = p.AuthenticationId
                WHERE a.IsSent = 1
                  AND p.IsImpressed = 1
                ORDER BY p.ImageId DESC
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            image_ids = [row[0] for row in rows]
            logging.info(f"IDs das imagens recuperados com sucesso: {image_ids}")
            return image_ids
        except Error as e:
            logging.error(f"Erro ao recuperar os dados do banco de dados: {e}")
            return []

    @staticmethod
    def update(image_id, cursor):
        """
        Atualiza o status `IsImpressed` de uma imagem no banco de dados.

        O status é primeiro definido como `0` e em seguida como `1` para o mesmo ID.

        :param image_id: ID da imagem a ser atualizada.
        :param cursor: Cursor ativo do banco de dados.
        """
        try:
            logging.info(f"Iniciando atualização do status `IsImpressed` para a imagem ID: {image_id}")
            cursor.execute("""UPDATE Portfolio SET IsImpressed = 0 WHERE ImageId = %s""", (image_id,))
            cursor.execute("""UPDATE Portfolio SET IsImpressed = 1 WHERE ImageId = %s""", (image_id,))
            logging.info(f"Status `IsImpressed` atualizado com sucesso para a imagem ID: {image_id}")
        except Error as e:
            logging.error(f"Erro ao atualizar a imagem com ID {image_id}: {e}")
