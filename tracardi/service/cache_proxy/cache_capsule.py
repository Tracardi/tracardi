from typing import Optional, Awaitable, Callable, List, Any, Dict

from pydantic import BaseModel


class CacheCapsule(BaseModel):
    ttl: int
    max_wait_between_calls: Optional[float] = 0
    max_no_exec_time: Optional[float] = 0
    func: Callable[..., Awaitable[Any]]
    func_args: List[Any] = []
    func_kwargs: Dict[str, Any] = {}

    def __hash__(self):
        key = (self.func, *self.func_args, frozenset(self.func_kwargs.items()))
        return hash(key)

    async def run(self):
        return await self.func(*self.func_args, **self.func_kwargs)