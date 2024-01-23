from tracardi.domain.named_entity import NamedEntity, NamedEntityInContext
from pydantic import field_validator
from typing import List, Optional
# from tracardi.service.secrets import encrypt, decrypt
import json
import re


class QueryBuildingError(Exception):
    pass


class Report(NamedEntityInContext):
    _regex = re.compile(r"\"\{{2}\s*([0-9a-zA-Z_]+)\s*\}{2}\"")
    description: str
    index: str
    query: dict
    tags: List[str]
    enabled: Optional[bool] = False

    @field_validator("index")
    @classmethod
    def validate_entity(cls, value):
        if value not in ("profile", "session", "event", "entity"):
            raise ValueError(f"Entity has to be one of: profile, session, event, entity. `{value}` given.")
        return value

    @staticmethod
    def _format_value(value) -> str:
        return f"\"{value}\"" if isinstance(value, str) else str(value)

    def get_built_query(self, **kwargs) -> dict:
        try:
            query = json.dumps(self.query)
            query = re.sub(
                self._regex,
                lambda x: self._format_value(kwargs[x.group(1)]),
                query
            )
            return json.loads(query)
        except KeyError as e:
            raise QueryBuildingError(f"Missing parameter: {str(e)}")

        except Exception as e:
            raise QueryBuildingError(str(e))

    @property
    def expected_query_params(self) -> List[str]:
        return re.findall(self._regex, json.dumps(self.query))

    def __eq__(self, other: 'Report') -> bool:
        return self.id == other.id \
               and json.dumps(self.query) == json.dumps(other.query) \
               and self.name == other.name \
               and self.index == other.index \
               and self.description == other.description \
               and self.tags == other.tags

