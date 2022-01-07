from typing import Any, Optional
from pydantic import BaseModel


class Result(BaseModel):
    port: str
    value: Any = None

    class Config:
        allow_mutation = False

    @staticmethod
    def append_input(result: 'Result', payload) -> Optional['Result']:
        if result is None:
            return None
        elif result.value is None:
            return Result(value=payload, port=result.port)
        elif isinstance(result.value, dict):
            payload.update(result.value)
            return Result(value=payload, port=result.port)
        else:
            return result


class MissingResult(Result):
    pass


class VoidResult(Result):
    pass
