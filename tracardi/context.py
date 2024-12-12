import json
from contextvars import ContextVar
from pydantic import BaseModel
from typing import Optional, Any
from uuid import uuid4


from tracardi.version import version as system_version
from tracardi.domain.user import User
from tracardi.service.singleton import Singleton
from tracardi.service.tracking.tracker_profiler import TrackerProfiler
from urllib.parse import parse_qs

ctx_id: ContextVar[str] = ContextVar("request_id", default="")

class ContextError(ValueError):
    pass

class Context:
    id: Optional[str] = None
    production: bool = system_version.production
    user: Optional[User] = None
    tenant: Optional[str] = None
    host: Optional[str] = None
    version: Optional[str] = None
    errors: int = 0
    warnings: int = 0
    event_type: Optional[str] = None
    metadata: Optional[dict] = None

    def __init__(self,
                 production: bool = None,
                 user: Optional[User] = None,
                 tenant: str = None,
                 host: Optional[str] = None,
                 version: Optional[str] = None,
                 metadata: Optional[dict] = None
                 ):

        self.version = version if version else system_version.version

        # This is every important: if not multi tenant replace tenant version by version name.
        if not system_version.multi_tenant:
            self.tenant = system_version.name
        else:
            if tenant is None:
                raise ValueError("Tenant is not set.")
            self.tenant = tenant

        self.user = user
        self.production = system_version.production if production is None else production
        self.host = host
        self.errors = 0
        self.warnings = 0
        self._profiler = TrackerProfiler()
        self.metadata = metadata

    @property
    def profiler(self) -> TrackerProfiler:
        return self._profiler

    def is_production(self) -> bool:
        return self.production

    def context_abrv(self) -> str:
        return 'p' if self.production else 't'

    def switch_context(self, production, user=None, tenant=None, metadata=None) -> 'Context':
        if user is None:
            user = self.user
        if tenant is None:
            tenant = self.tenant
        if metadata is None:
            metadata = self.metadata
        return Context(production=production, user=user, tenant=tenant, metadata=metadata)

    def get_user_less_context_copy(self) -> 'Context':
        return Context(
            production=self.production,
            user=None,
            tenant=self.tenant,
            host=self.host,
            version=self.version
        )

    @staticmethod
    def _parse_body(body: bytes) -> dict:
        """Parse JSON body or return raw data."""
        if not body:
            return {}
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {"raw": body.decode("utf-8", errors="ignore")}

    def get_metadata(self):

        if not self.metadata:
            return {
                "path": None,
                "params": {},
                # "body": self._parse_body(self.metadata["body"].decode('utf-8')),
                "body": "",
                "headers": {}
            }

        return {
            "path": self.metadata["path"],
            "params": parse_qs(self.metadata['params'].decode('utf-8')),
            # "body": self._parse_body(self.metadata["body"].decode('utf-8')),
            "body": "",
            "headers": {key.decode("utf-8"): value.decode("utf-8") for key, value in self.metadata["headers"]}
        }

    def __str__(self):
        return f"Context(mode: {'production' if self.production else 'sand-box'}, " \
               f"user: {str(self.user)}, " \
               f"tenant: {self.tenant}, " \
               f"version: {self.version}, " \
               f"event: {self.event_type}, " \
               f"host: {self.host}), " \
               f"metadata: {self.metadata})"

    def __repr__(self):
        return f"Context(mode: {'production' if self.production else 'sand-box'}, " \
               f"user: {str(self.user)}, " \
               f"tenant: {self.tenant}, " \
               f"version: {self.version}, " \
               f"event: {self.event_type}, " \
               f"host: {self.host}), " \
               f"metadata: {self.metadata})"

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
            raise ContextError("No context is set.")
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
