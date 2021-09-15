from tracardi.service.singleton import Singleton
from tracardi.config import tracardi
from tracardi.service.storage.drivers.elastic_driver import ElasticDriver


class Storage(object, metaclass=Singleton):

    def __init__(self):
        self.types = {
            'elastic': ElasticDriver()
        }
        self._driver = self.types[tracardi.storage_driver]

    @property
    def driver(self):
        return self._driver


storage = Storage()
