from contextlib import asynccontextmanager

from tracardi.cluster_config import is_save_logs_on
from tracardi.config import tracardi
from tracardi.service.utils.date import now_in_utc
from logging import Handler, LogRecord
from time import time


class ElasticLogHandler(Handler):

    def __init__(self, level=0, collection=None):
        super().__init__(level)
        if collection is None:
            collection = []
        self.collection = collection
        self.last_save = time()

    def _get(self, record, value, default_value):
        return record.__dict__.get(value, default_value)

    def emit(self, record: LogRecord):

        # Skip info and debug.
        if record.levelno <= 25:
            return

        log = {  # Maps to tracardi-log index
            "date": now_in_utc(),
            "message": record.msg,
            "logger": record.name,
            "file": record.filename,
            "line": record.lineno,
            "level": record.levelname,
            "stack_info": record.stack_info,
            # "exc_info": record.exc_info  # Can not save this to TrackerPayload
            "module": self._get(record, "package", record.module),
            "class_name": self._get(record, "class_name", record.funcName),
            "origin": self._get(record, "origin", "root"),
            "event_id": self._get(record, "event_id", None),
            "profile_id": self._get(record, "profile_id", None),
            "flow_id": self._get(record, "flow_id", None),
            "node_id": self._get(record, "node_id", None),
            "user_id": self._get(record, "user_id", None),
        }

        self.collection.append(log)

    def has_logs(self, min_log_size=500):
        if not isinstance(self.collection, list):
            return False
        return len(self.collection) >= min_log_size or (time() - self.last_save) > 60

    def reset(self):
        self.collection = []
        self.last_save = time()


@asynccontextmanager
async def log_controller(log_handler: ElasticLogHandler) -> list:
    if tracardi.save_logs and log_handler.has_logs():
        try:
            if await is_save_logs_on():
                yield log_handler.collection
        finally:
            log_handler.reset()
