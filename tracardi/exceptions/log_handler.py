import os

import logging

from tracardi.exceptions.storage.elastic import ElasticLogHandler
from tracardi.service.logging.formater import CustomFormatter
from tracardi.service.logging.tools import _get_logging_level

_env = os.environ
_logging_level = _get_logging_level(_env['LOGGING_LEVEL']) if 'LOGGING_LEVEL' in _env else logging.WARNING


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
