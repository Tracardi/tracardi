from dataclasses import dataclass

import asyncio

from tracardi.context import Context
from tracardi.service.storage.index import Resource

from tracardi.worker.domain.migration_schema import MigrationSchema
from tracardi.worker.service.worker.migration_workers import copy_to_mysql

@dataclass
class Request:
    id: str

@dataclass
class Job:
    request: Request

    def update_state(self, *args, **kwargs):
        pass

async def main():
    schema = {
        "id": "b3a6edcfccd727f7392f87fd0c2476a2b85a3d4f",
        "copy_index": {
          "from_index": "static-0820.ffe49.tracardi-bridge",
          "to_index": "bridge",
          "multi": False,
          "script": None
        },
        "params": {
            "mysql": "bridge"
        },
        "worker": "copy_to_mysql",
        "asynchronous": True
      }
    job = Job(request=Request(id="1"))
    await copy_to_mysql(job, MigrationSchema(**schema), 'http://localhost:9200', Context(production=False))

asyncio.run(main())