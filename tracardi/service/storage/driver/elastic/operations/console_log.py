from tracardi.service.console_log import ConsoleLog
from tracardi.service.storage.driver.elastic import console_log as console_log_db


async def save_console_log(console_log: ConsoleLog):
    # Save console log
    encoded_console_log = list(console_log.get_encoded())
    if encoded_console_log:
        # Save in background
        await console_log_db.save_all(encoded_console_log)
