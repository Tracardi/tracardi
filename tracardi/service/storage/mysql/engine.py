from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from tracardi.config import mysql
from tracardi.service.singleton import Singleton


class AsyncMySqlEngine(metaclass=Singleton):

    def __init__(self, echo: bool = None):
        self.default = None
        self.engines = {}
        self.echo = mysql.mysql_echo if echo is None else echo

    @staticmethod
    def get_session(async_engine):
        return sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    def get_engine(self):
        if self.default is None:
            self.default = create_async_engine(
                mysql.mysql_database_uri,
                pool_size=3,
                max_overflow=2,
                pool_timeout=10,
                pool_recycle=1800,
                echo=self.echo)
        return self.default

    def get_engine_for_database(self):
        if mysql.mysql_database not in self.engines:
            db_url = f"{mysql.mysql_database_uri}/{mysql.mysql_database}"
            self.engines[mysql.mysql_database] = create_async_engine(
                db_url,
                pool_size=3,
                max_overflow=2,
                pool_timeout=10,
                pool_recycle=1800,
                echo=self.echo)
        return self.engines[mysql.mysql_database]
