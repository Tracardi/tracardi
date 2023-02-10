from contextvars import ContextVar
from typing import Optional, Any
from uuid import uuid4

from pydantic import BaseModel

from tracardi.config import tracardi
from tracardi.domain.user import User
from tracardi.service.singleton import Singleton

ctx_id: ContextVar[str] = ContextVar("request_id", default=None)


class Context(BaseModel):
    production: bool = tracardi.version.production
    user: Optional[User] = None

    def is_production(self) -> bool:
        return self.production

    def switch_context(self, production, user=None) -> 'Context':
        if user is None:
            user = self.user
        return Context(production=production, user=user)

    def __str__(self):
        return f"Context(on {'production' if self.production else 'staging'} as user: {self.user.full_name if self.user else 'Unknown'})"

    def __repr__(self):
        return f"Context(on {'production' if self.production else 'staging'} as user: {self.user.full_name if self.user else 'Unknown'})"


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


def set_context(ctx: Context):
    cm = ContextManager()
    return cm.set("request-context", ctx)


class ServerContext:
    ctx_handler: Any

    def __init__(self, context: Context):
        self.cm = ContextManager()
        self.context = context

    def __enter__(self):
        self.ctx_handler = ctx_id.set(str(uuid4()))
        set_context(self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cm.reset()
        ctx_id.reset(self.ctx_handler)

    def get_context(self):
        return self.cm.get("request-context")

    @staticmethod
    def get_context_id():
        return ctx_id.get()
