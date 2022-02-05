from datetime import datetime
from logging import Handler, LogRecord


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

    def has_logs(self):
        return isinstance(self.collection, list) and len(self.collection) > 0

    def reset(self):
        self.collection = []


log_handler = ElasticLogHandler()
