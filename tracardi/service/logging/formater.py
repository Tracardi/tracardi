import json
import logging


class CustomFormatter(logging.Formatter):
    white = "\x1b[97m"
    grey = "\x1b[37m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s [%(levelname)s] %(message)s | %(name)s | %(filename)s | %(lineno)d"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: white + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.format)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class ConsoleFormatter(logging.Formatter):
    format = "%(asctime)s [%(levelname)s] %(message)s | %(name)s | %(filename)s | %(lineno)d"

    FORMATS = {
        logging.DEBUG: format,
        logging.INFO: format,
        logging.WARNING: format,
        logging.ERROR: format,
        logging.CRITICAL: format
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.format)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class JSONFormatter(logging.Formatter):
    def format(self, record):
        # Ensure asctime and message are computed
        record.asctime = self.formatTime(record, self.datefmt)
        record.message = record.getMessage()

        log_record = {
            "timestamp": record.asctime,
            "level": record.levelname,
            "message": record.message,
            "name": record.name,
            "filename": record.filename,
            "lineno": record.lineno,
        }
        return json.dumps(log_record)
