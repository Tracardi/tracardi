from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from tracardi.service.singleton import Singleton


class AsyncMySqlEngine(metaclass=Singleton):

    def __init__(self):
        self.default = None
        self.engines = {}
        self.echo = True

    def get_session(self, async_engine):
        return sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    def get_engine(self):
        if self.default is None:
            ASYNC_DB_URL = f"mysql+aiomysql://root:root@localhost"
            self.default = create_async_engine(ASYNC_DB_URL, echo=self.echo)
        return self.default

    def get_engine_for_database(self, database: str):
        if database not in self.engines:
            ASYNC_DB_URL = f"mysql+aiomysql://root:root@localhost/{database}"
            self.engines[database] = create_async_engine(ASYNC_DB_URL, echo=self.echo)
        return self.engines[database]
