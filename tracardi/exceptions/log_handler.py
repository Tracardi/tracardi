import os

import logging

from tracardi.service.logging.formater import CustomFormatter
from tracardi.service.logging.tools import _get_logging_level
from tracardi.service.utils.date import now_in_utc
from logging import Handler, LogRecord
from time import time

_env = os.environ
_logging_level = _get_logging_level(_env['LOGGING_LEVEL']) if 'LOGGING_LEVEL' in _env else logging.WARNING
_save_logs_on = _env.get('SAVE_LOGS', 'yes').lower() == 'yes'

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

        if _save_logs_on:
            self.collection.append(log)

    def has_logs(self):
        return _save_logs_on is True and isinstance(self.collection, list)

    def reset(self):
        self.collection = []
        self.last_save = time()


class StackInfoLogger(logging.Logger):
    def error(self, msg, *args, **kwargs):
        kwargs['stack_info'] = True
        kwargs['exc_info'] = True
        super().error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        kwargs['stack_info'] = True
        kwargs['exc_info'] = True
        super().error(msg, *args, **kwargs)


logging.setLoggerClass(StackInfoLogger)
logging.basicConfig(level=logging.INFO)

def get_logger(name, level=None):
    # Replace the default logger class with your custom class
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(level or _logging_level)

    # Elastic log formatter

    logger.addHandler(log_handler)

    # Console log handler

    clh = logging.StreamHandler()
    clh.setFormatter(CustomFormatter())
    logger.addHandler(clh)

    return logger


def get_installation_logger(name, level=None):
    # Replace the default logger class with your custom class
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(level or _logging_level)

    # Console log handler

    clh = logging.StreamHandler()
    clh.setFormatter(CustomFormatter())
    logger.addHandler(clh)

    return logger


log_handler = ElasticLogHandler()
