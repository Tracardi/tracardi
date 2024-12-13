from typing import Optional, Awaitable, Callable, List, Any, Dict

from pydantic import BaseModel


class CacheCapsule(BaseModel):
    ttl: int
    throttle: Optional[float] = 0
    func: Callable[..., Awaitable[Any]]
    func_args: List[Any] = []
    func_kwargs: Dict[str, Any] = {}

    def key(self) -> str:
        key = (self.func, *self.func_args, frozenset(self.func_kwargs.items()))
        return str(hash(key))