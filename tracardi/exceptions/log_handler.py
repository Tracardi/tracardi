from tracardi.service.utils.date import now_in_utc
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
            "date": now_in_utc(),
            "message": record.msg,
            "logger": record.name,
            "file": record.filename,
            "line": record.lineno,
            "level": record.levelname,
            "stack_info": record.stack_info,
            # "exc_info": record.exc_info  # Can not save this to TrackerPayload
        }

        if tracardi.save_logs:
            self.collection.append(log)

    def get_errors(self):
        return [log for log in self.collection if log['level'] == "ERROR"]

    def has_logs(self):
        return tracardi.save_logs is True and isinstance(self.collection, list)

    def reset(self):
        self.collection = []
        self.last_save = time()


log_handler = ElasticLogHandler()
