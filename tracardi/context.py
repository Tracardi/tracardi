from contextvars import ContextVar
from typing import Optional, Any
from uuid import uuid4

from pydantic import BaseModel

from tracardi.config import tracardi
from tracardi.domain.user import User
from tracardi.service.singleton import Singleton

ctx_id: ContextVar[str] = ContextVar("request_id", default="")


class Context:

    production: bool = tracardi.version.production
    user: Optional[User] = None
    tenant: str
    host: Optional[str] = None

    def __init__(self,
                 production:bool = None,
                 user: Optional[User] = None,
                 tenant: str = None,
                 host: Optional[str] = None):

        # This is every important: if not multi tenant replace tenant version by version name.
        if not tracardi.multi_tenant:
            self.tenant = tracardi.version.name
        else:
            self.tenant = tenant

        self.user = user
        self.production = tracardi.version.production if production is None else production
        self.host = host

    def is_production(self) -> bool:
        return self.production

    def switch_context(self, production, user=None, tenant=None) -> 'Context':
        if user is None:
            user = self.user
        if tenant is None:
            tenant = self.tenant
        return Context(production=production, user=user, tenant=tenant)

    def __str__(self):
        return f"Context(mode: {'production' if self.production else 'staging'}, " \
               f"user: {self.user.full_name if self.user else 'Unknown'}, " \
               f"tenant: {self.tenant}, " \
               f"host: {self.host})"

    def __repr__(self):
        return f"Context(mode: {'production' if self.production else 'staging'}, " \
               f"user: {self.user.full_name if self.user else 'Unknown'}, " \
               f"tenant: {self.tenant}, " \
               f"host: {self.host})"

    def __hash__(self):
        return hash((self.production, self.tenant))

    def __eq__(self, other):
        if isinstance(other, Context):
            return (self.production, self.tenant) == (other.production, other.tenant)
        return False


class ContextManager(metaclass=Singleton):

    def __init__(self):
        self._store = {}

    def _empty(self):
        var = ctx_id.get()
        return var is None or var not in self._store

    def get(self, var):
        if self._empty():
            raise ValueError("No context is set.")
        _request_id = ctx_id.get()
        store = self._store[_request_id]
        context = store.get(var, None)

        if not context:
            raise ValueError("No context is set. Can't get context.")

        return context

    def set(self, var, value):
        _request_id = ctx_id.get()
        if self._empty():
            self._store[_request_id] = {}

        self._store[_request_id][var] = value

    def reset(self):
        _request_id = ctx_id.get()
        if _request_id in self._store:
            del self._store[_request_id]


def get_context() -> Context:
    cm = ContextManager()
    return cm.get("request-context")


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

    def get_context(self) -> Context:
        return self.cm.get("request-context")

    @staticmethod
    def get_context_id():
        return ctx_id.get()
