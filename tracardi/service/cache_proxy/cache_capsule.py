from typing import Optional, Awaitable, Callable, List, Any, Dict

from pydantic import BaseModel


class CacheCapsule(BaseModel):
    cache_ttl: int
    max_no_exec_time: Optional[float] = 0
    func: Callable[..., Awaitable[Any]]
    func_args: List[Any] = []
    func_kwargs: Dict[str, Any] = {}

    def __init__(self, /, **data: Any):
        super().__init__(**data)
        if self.max_no_exec_time < self.cache_ttl:
            raise ValueError(f"The maximum execution time cannot be shorter than the cache duration. If the function is cached, it will not even be considered for execution.")

    def __hash__(self):
        key = (f"{self.func.__module__}.{self.func.__name__}", *self.func_args, frozenset(self.func_kwargs.items()))
        return hash(key)

    async def run(self):
        return await self.func(*self.func_args, **self.func_kwargs)
