import psycopg2


class PostgresConnection:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self, dbname, user, password, host, port):
        print("[DB] Подключение к PostgreSQL...")
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.conn.cursor()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            print("[DB] Соединение закрыто.")

    def get_cursor(self):
        return self.cursor

    def get_connection(self):
        return self.conn


# Глобальный экземпляр
pg = PostgresConnection()
