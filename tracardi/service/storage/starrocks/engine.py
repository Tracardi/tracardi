from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from tracardi.config import mysql, starrocks
from tracardi.service.singleton import Singleton


class AsyncStarRocksEngine(metaclass=Singleton):

    def __init__(self, echo: bool = None):
        self.default = None
        self.engines = {}
        self.echo = True  # starrocks.starrocks_echo if echo is None else echo

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
                starrocks.starrocks_database_uri,
                pool_size=3,
                max_overflow=2,
                pool_timeout=10,
                pool_recycle=1800,
                echo=self.echo)
        return self.default

    def get_engine_for_database(self):
        if starrocks.starrocks_database not in self.engines:
            db_url = f"{starrocks.starrocks_database_uri}/{starrocks.starrocks_database}"
            self.engines[starrocks.starrocks_database] = create_async_engine(
                db_url,
                pool_size=3,
                max_overflow=2,
                pool_timeout=10,
                pool_recycle=1800,
                echo=self.echo)
        return self.engines[starrocks.starrocks_database]
