import os

from tracardi.service.logging.formater import CustomFormatter, JSONFormatter, ConsoleFormatter


def log_format_adapter():
    type = os.environ.get('LOGGING_FORMAT', 'console')
    if type == 'console':
        return ConsoleFormatter()
    elif type == 'json':
        return JSONFormatter()
    else:
        return CustomFormatter()