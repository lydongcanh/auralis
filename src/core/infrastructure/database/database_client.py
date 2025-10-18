import psycopg

from core.utils.env import get_required_env

class DatabaseClient:
    def __init__(self):
        self.connection = None

    def connect(self):
        DATABASE_URL = get_required_env("DATABASE_URL")
        self.connection = psycopg.connect(DATABASE_URL)

    def close(self):
        if self.connection:
            self.connection.close()
