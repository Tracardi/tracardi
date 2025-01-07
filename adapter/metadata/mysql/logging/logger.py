import logging


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


def get_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.hasHandlers():  # Avoid duplicate handlers
        handler = logging.StreamHandler()
        handler.setFormatter(ConsoleFormatter())
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger
