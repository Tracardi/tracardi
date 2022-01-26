from datetime import datetime
from logging import Handler, LogRecord

from tracardi.exceptions.exception import StorageException
from tracardi.service.storage.driver import storage


class ElasticLogHandler(Handler):

    def __init__(self, level=0, collection=None):
        super().__init__(level)

        if collection is None:
            collection = []
        self.collection = collection

    def emit(self, record: LogRecord):
        record = {
            "date": datetime.utcnow(),
            "message": record.msg,
            "logger": record.name,
            "file": record.filename,
            "line": record.lineno,
            "level": record.levelname
        }

        self.collection.append(record)

    async def save(self):
        try:
            if isinstance(self.collection, list) and len(self.collection) > 0:
                await storage.driver.raw.collection('log', self.collection).save()
                self.collection = []
        except StorageException as e:
            print(str(e))


log_handler = ElasticLogHandler()
