from contextvars import ContextVar
from dataclasses import dataclass
from typing import Optional, Any
from uuid import uuid4

from tracardi.config import tracardi
from tracardi.domain.user import User
from tracardi.service.singleton import Singleton

ctx_id: ContextVar[str] = ContextVar("request_id", default=None)


@dataclass
class Context:
    production: bool = tracardi.version.production
    user: Optional[User] = None

    def is_production(self) -> bool:
        if self.production:
            # only admin can have context production
            if self.user and self.user.is_admin() and not self.user.is_expired():
                return True

        return False


class ContextManager(metaclass=Singleton):

    def __init__(self):
        self._store = {}

    def _empty(self):
        var = ctx_id.get()
        return var is None or var not in self._store

    def get(self, var, default=None):
        if self._empty():
            return default
        _var = ctx_id.get()
        store = self._store[_var]
        return store.get(var, default)

    def set(self, var, value):
        _var = ctx_id.get()
        if self._empty():
            self._store[_var] = {}

        self._store[_var][var] = value

    def reset(self):
        _var = ctx_id.get()
        if _var in self._store:
            del self._store[_var]


def get_context() -> Context:
    cm = ContextManager()
    return cm.get("request-context", Context())


class ServerContext:
    ctx_handler: Any

    def __init__(self, context: Context):
        self.cm = ContextManager()
        self.context = context

    def __enter__(self):
        self.ctx_handler = ctx_id.set(str(uuid4()))
        self.cm.set("request-context", self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cm.reset()
        ctx_id.reset(self.ctx_handler)

    def get_context(self):
        return self.cm.get("request-context")



