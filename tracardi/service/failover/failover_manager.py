from time import sleep
from uuid import uuid4
from typing import Callable, List, Union

from tracardi.context import Context
from tracardi.service.storage.speedb.rocksdb_clinet import RocksDbClient


class FailOverManager:

    def __init__(self, db_name, sleep_on_failure:int=3):
        self.db_client = RocksDbClient(db_name)
        self.db_client.create_storage()
        self._sleep_on_failure = sleep_on_failure

    def add(self, context, data, options):
        self.db_client.add_record(str(uuid4()), (context, data, options))

    def sync(self):
        self.db_client.sync()

    def is_empty(self) -> bool:
        return self.db_client.is_empty()

    def flush(self, closure: Callable):
        print("Thread flushing failed records has started.")
        for key, value in self.db_client.get_all_records():

            # Stored value always contains data and options how to send it
            context, data, options = value

            if closure(context, data, options):
                self.db_client.delete_record(key)
            else:
                # Wait
                sleep(self._sleep_on_failure)
        print("Thread flushing failed records has been finished.")
