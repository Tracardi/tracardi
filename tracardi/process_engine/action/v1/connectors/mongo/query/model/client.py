from motor.motor_asyncio import AsyncIOMotorClient
from .configuration import MongoConfiguration


class MongoClient:
    def __init__(self, config: MongoConfiguration):
        self.config = config
        self.client = AsyncIOMotorClient(config.uri, serverSelectionTimeoutMS=config.timeout)

    async def find(self, database, collection, query):
        database = self.client[database]
        collection = database[collection]
        return [data async for data in collection.find(query)]

    async def dbs(self):
        return await self.client.list_database_names()

    async def collections(self, database):
        database = self.client[database]
        return await database.list_collection_names()

    async def close(self):
        if self.client:
            await self.client.close()
