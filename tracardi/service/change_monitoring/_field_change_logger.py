# from time import time
#
# from typing import Optional, Dict, List
#
#
# class FieldChangeLogger:
#
#     def __init__(self, init=None):
#         if init is None:
#             self._log = {}
#         else:
#             self._log = init
#     def log(self, field, old_value: Optional[str] = None):
#         self._log[field] = [time(), old_value]
#
#     def merge(self, other):
#         self._log.update(other.get_log())
#         return self
#
#     def get_log(self) -> Dict[str, List]:
#         return self._log
#
#     def empty(self) -> bool:
#         return not self._log
#
#     def convert_to_list(self, extend_with_values=None):
#         result = []
#         for field, (timestamp, old_value) in self._log.items():
#             data = {"field": field, "timestamp": timestamp, "old_value": old_value}
#             if extend_with_values:
#                 data.update(extend_with_values)
#             result.append(data)
#         return result
#
