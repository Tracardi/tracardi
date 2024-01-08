from typing import Any, Optional, Tuple, Union
from pydantic import ConfigDict, BaseModel


class Result(BaseModel):
    port: str
    value: Optional[dict] = None
    model_config = ConfigDict(frozen=True)

    @staticmethod
    def append_input(result: Union['Result', Tuple['Result', ...]], payload) -> Optional[Union['Result', Tuple['Result', ...]]]:
        if result is None:  # Is empty
            return None
        elif isinstance(result, tuple):  # Has multiple outputs
            results = []
            for r in result:
                if isinstance(r, Result) and isinstance(r.value, dict):
                    payload.update(r.value)
                    results.append(Result(value=payload, port=r.port))
            return tuple(results)
        elif isinstance(result, Result) and result.value is None:  # Has empty value
            return Result(value=None, port=result.port)
        elif isinstance(result, Result) and isinstance(result.value, dict):
            payload.update(result.value)
            return Result(value=payload, port=result.port)
        else:
            return result


class MissingResult(Result):
    pass


class VoidResult(Result):
    pass
