from tracardi.domain.named_entity import NamedEntity
from typing import List
from tracardi.service.secrets import encrypt, decrypt
import json
import re


class QueryBuildingError(Exception):
    pass


class ReportRecord(NamedEntity):
    description: str
    entity: str
    query: str
    tags: List[str]


class Report(NamedEntity):
    _regex = re.compile(r"\"\{{2}\s*([0-9a-zA-Z_]+)\s*\}{2}\"")
    description: str
    entity: str
    query: dict
    tags: List[str]

    def encode(self) -> ReportRecord:
        return ReportRecord(
            id=self.id,
            name=self.name,
            description=self.description,
            tags=self.tags,
            entity=self.entity,
            query=encrypt(self.query)
        )

    @staticmethod
    def decode(record: ReportRecord) -> 'Report':
        return Report(
            id=record.id,
            name=record.name,
            description=record.description,
            entity=record.entity,
            tags=record.tags,
            query=decrypt(record.query)
        )

    @staticmethod
    def _format_value(value) -> str:
        return f"\"{value}\"" if isinstance(value, str) else value

    def get_built_query(self, **kwargs) -> dict:
        query = json.dumps(self.query)
        query = re.sub(
            self._regex,
            lambda x: self._format_value(kwargs[x.group(1)]),
            query
        )
        return json.loads(query)

