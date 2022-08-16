from datetime import datetime
from logging import Handler, LogRecord
from time import time
from tracardi.config import tracardi


class ElasticLogHandler(Handler):

    def __init__(self, level=0, collection=None):
        super().__init__(level)

        if collection is None:
            collection = []
        self.collection = collection
        self.last_save = time()

    def emit(self, record: LogRecord):
        log = {
            "date": datetime.utcnow(),
            "message": record.msg,
            "logger": record.name,
            "file": record.filename,
            "line": record.lineno,
            "level": record.levelname,
            # "stack_info": record.stack_info,
            # "exc_info": record.exc_info  # Can not save this to TrackerPayload
        }

        if tracardi.save_logs or tracardi.monitor_logs_event_type:
            self.collection.append(log)

    def has_logs(self):
        return tracardi.save_logs is True and isinstance(self.collection, list) and (
                len(self.collection) > 100 or (time() - self.last_save) > 30)

    def reset(self):
        self.collection = []
        self.last_save = time()


log_handler = ElasticLogHandler()
