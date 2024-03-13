# import os
# from speedict import Rdict
#
# from tracardi.exceptions.log_handler import get_logger
#
# logger = get_logger(__name__)
#
#
# class RocksDbClient:
#
#     def __init__(self, db_name: str):
#         self.storage_path = f'/opt/tracardi/{db_name}'
#         self.db = None
#
#     def check_storage(self) -> bool:
#         return self.db and os.path.exists(self.storage_path)
#
#     def create_storage(self) -> bool:
#         try:
#             os.makedirs(self.storage_path, exist_ok=True)
#             self.db = Rdict(self.storage_path)
#
#             return True
#         except OSError as e:
#             logger.error(str(e), e, exc_info=True)
#             return False
#
#     def open_storage(self):
#         self.db = Rdict(self.storage_path)
#
#     def destroy_storage(self):
#         self.db.close()
#         self.db.destroy(self.storage_path)
#
#     def close_storage(self):
#         self.db.close()
#
#
#     def sync(self):
#         self.db.flush()
#
#     def add_record(self, key, value):
#         self.db[key] = value
#
#     def delete_record(self, key):
#         self.db.delete(key)
#
#     def get_all_records(self, limit: int = None):
#         i = 0
#         for k, v in self.db.items():
#             i += 1
#             if limit and i > limit:
#                 break
#             yield k, v
#
#     def is_empty(self) -> bool:
#         for _, _ in self.db.items():
#             return False
#         return True
#
#     def __contains__(self, item):
#         return item in self.db
#
#     def __getitem__(self, item):
#         return self.db[item]
#
#     def __setitem__(self, key, value):
#         self.db[key] = value
