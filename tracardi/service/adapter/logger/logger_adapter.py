import os

from tracardi.service.logging.formater import CustomFormatter, JSONFormatter

def log_format_adapter():
    type = os.environ.get('LOGGING_FORMAT', 'console')

    if type == 'console':
        return CustomFormatter()
    elif type == 'json':
        return JSONFormatter()