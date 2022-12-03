from dataclasses import dataclass
from typing import List

from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult


@dataclass
class CollectResult:
    session: List[BulkInsertResult]
    events: List[BulkInsertResult]
    profile: List[BulkInsertResult]
