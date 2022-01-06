import aiomysql
import asyncio
from pydantic import BaseModel


class Connection(BaseModel):
    database: str
    user: str
    password: str = None
    host: str
    port: int = 3306

    async def connect(self, timeout=None):
        loop = asyncio.get_event_loop()
        return await aiomysql.create_pool(host=self.host, port=self.port,
                                          user=self.user, password=self.password,
                                          db=self.database, loop=loop,
                                          connect_timeout=timeout)
