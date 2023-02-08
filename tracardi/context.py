from contextvars import ContextVar
from dataclasses import dataclass
from typing import Optional

from tracardi.domain.user import User


@dataclass
class Context:
    scope: str = None
    user: Optional[User] = None

    def context(self):
        if self.scope == 'production':
            # only admin can have context production
            if self.user and self.user.is_admin() and not self.user.is_expired():
                return 'production'

        return 'staging'


CTX_KEY = "x-context"

ctx_var: ContextVar[str] = ContextVar(CTX_KEY, default=Context())


def get_context() -> Context:
    return ctx_var.get()
