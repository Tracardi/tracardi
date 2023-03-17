import asyncio

from tracardi.service.console_log import ConsoleLog
from tracardi.service.storage.driver import storage


def save_console_log(console_log: ConsoleLog):
    # Save console log
    encoded_console_log = list(console_log.get_encoded())
    if encoded_console_log:
        # Save in background
        asyncio.create_task(storage.driver.console_log.save_all(encoded_console_log))
