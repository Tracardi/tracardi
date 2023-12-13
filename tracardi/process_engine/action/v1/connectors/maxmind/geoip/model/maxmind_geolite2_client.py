from typing import Optional

import geoip2.database
import geoip2.webservice

import os
from pydantic import BaseModel
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.singleton import Singleton
from tracardi.service.plugin.domain.config import PluginConfig


class PluginConfiguration(PluginConfig):
    source: NamedEntity
    ip: str
    add_to_profile: Optional[bool] = False


class GeoLiteCredentials(BaseModel):
    accountId: int
    license: str
    host: str = 'geolite.info'


class GeoIpConfiguration(BaseModel):
    webservice: GeoLiteCredentials = None
    database: str = None

    def get_local_database(self):
        return os.path.join(self.database)

    def is_local(self):
        return self.database is not None

    def is_remote(self):
        return self.webservice is not None


class MaxMindGeoLite2Client:

    def __init__(self, credentials: GeoLiteCredentials):
        self.client = geoip2.webservice.AsyncClient(credentials.accountId, credentials.license, host=credentials.host)

    async def read(self, ip: str):
        return await self.client.city(ip)

    async def close(self):
        await self.client.close()


class MaxMindGeoLite2Reader(metaclass=Singleton):

    def __init__(self, database):
        self.reader = geoip2.database.Reader(database)

    def read(self, ip: str):
        return self.reader.city(ip)

    def __del__(self):
        if self.reader:
            self.reader.close()


class MaxMindGeoLite2:

    def __init__(self, config: GeoIpConfiguration):
        self.config = config
        if self.config.is_local():
            self.client = MaxMindGeoLite2Reader(database=self.config.get_local_database())
        elif self.config.is_remote():
            self.client = MaxMindGeoLite2Client(credentials=self.config.webservice)
        else:
            raise ValueError("Misconfiguration of MaxMindGeoLite2.")

    async def fetch(self, ip):
        result = self.client.read(ip)
        if isinstance(self.client, MaxMindGeoLite2Client):
            result = await result
            await self.client.close()
        return result
