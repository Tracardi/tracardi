# from time import sleep
# from uuid import uuid4
# from typing import Callable, Dict
#
# from tracardi.exceptions.log_handler import get_logger
# from tracardi.service.storage.speedb.rocksdb_clinet import RocksDbClient
#
# logger = get_logger(__name__)
#
# class FailOverManager:
#
#     dbs: Dict[str, RocksDbClient] = {}
#
#     def __init__(self, db_name, sleep_on_failure:int=3):
#         if db_name not in self.dbs:
#             client = RocksDbClient(db_name)
#             client.create_storage()
#             self.dbs[db_name] = client
#
#         self.db_client = self.dbs[db_name]
#         self._sleep_on_failure = sleep_on_failure
#
#     def add(self, context, data, options):
#         self.db_client.add_record(str(uuid4()), (context, data, options))
#
#     def sync(self):
#         self.db_client.sync()
#
#     def is_empty(self) -> bool:
#         return self.db_client.is_empty()
#
#     def flush(self, closure: Callable):
#         logger.info("Thread flushing failed records has started.")
#         for key, value in self.db_client.get_all_records():
#
#             # Stored value always contains data and options how to send it
#             context, data, options = value
#
#             if closure(context, data, options):
#                 self.db_client.delete_record(key)
#             else:
#                 # Wait
#                 sleep(self._sleep_on_failure)
#         logger.info("Thread flushing failed records has been finished.")
