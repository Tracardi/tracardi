from contextvars import ContextVar
from pydantic import BaseModel
from typing import Optional, Any
from uuid import uuid4

from tracardi.config import tracardi
from tracardi.domain.user import User
from tracardi.service.singleton import Singleton

ctx_id: ContextVar[str] = ContextVar("request_id", default="")


class Context:
    id: Optional[str] = None
    production: bool = tracardi.version.production
    user: Optional[User] = None
    tenant: Optional[str] = None
    host: Optional[str] = None
    version: Optional[str] = None
    errors: int = 0
    warnings: int = 0

    def __init__(self,
                 production: bool = None,
                 user: Optional[User] = None,
                 tenant: str = None,
                 host: Optional[str] = None,
                 version: Optional[str] = None
                 ):

        self.version = version if version else tracardi.version.version

        # This is every important: if not multi tenant replace tenant version by version name.
        if not tracardi.multi_tenant:
            self.tenant = tracardi.version.name
        else:
            if tenant is None:
                raise ValueError("Tenant is not set.")
            self.tenant = tenant

        self.user = user
        self.production = tracardi.version.production if production is None else production
        self.host = host
        self.errors = 0
        self.warnings = 0

    def is_production(self) -> bool:
        return self.production

    def context_abrv(self) -> str:
        return 'p' if self.production else 't'

    def switch_context(self, production, user=None, tenant=None) -> 'Context':
        if user is None:
            user = self.user
        if tenant is None:
            tenant = self.tenant
        return Context(production=production, user=user, tenant=tenant)

    def get_user_less_context_copy(self) -> 'Context':
        return Context(
            production=self.production,
            user=None,
            tenant=self.tenant,
            host=self.host,
            version=self.version
        )

    def __str__(self):
        return f"Context(mode: {'production' if self.production else 'staging'}, " \
               f"user: {str(self.user)}, " \
               f"tenant: {self.tenant}, " \
               f"version: {self.version}, " \
               f"host: {self.host})"

    def __repr__(self):
        return f"Context(mode: {'production' if self.production else 'staging'}, " \
               f"user: {str(self.user)}, " \
               f"tenant: {self.tenant}, " \
               f"version: {self.version}, " \
               f"host: {self.host})"

    def __hash__(self):
        return hash((self.production, self.tenant))

    def __eq__(self, other):
        if isinstance(other, Context):
            return (self.production, self.tenant) == (other.production, other.tenant)
        return False

    def dict(self, without_user:bool=False) -> dict:
        return {
            "production": self.production,
            "user": self.user.model_dump(mode='json') if not without_user and isinstance(self.user, BaseModel) else None,
            "tenant": self.tenant,
            "host": self.host,
            "version": self.version
        }

    @staticmethod
    def from_dict(context: dict) -> 'Context':
        return Context(
            production=context.get('production', False),
            user=context.get('user', None),
            tenant=context.get('tenant'),
            host=context.get('host'),
            version=context.get('version')
        )

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

    def set(self, local: str, context: Context):
        if not isinstance(context, Context):
            raise ValueError(f"Expected Context object got {type(context)}")

        _request_id = ctx_id.get()

        if self._empty():
            context.id = _request_id
            self._store[_request_id] = {}

        self._store[_request_id][local] = context

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
        if self.context is not None:
            self.ctx_handler = ctx_id.set(str(uuid4()))
            self.cm.set("request-context", self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.context is not None:
            self.cm.reset()
            ctx_id.reset(self.ctx_handler)

    def get_context(self) -> Context:
        return self.cm.get("request-context")

    @staticmethod
    def get_context_id():
        return ctx_id.get()
