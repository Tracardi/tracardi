from hashlib import md5
from typing import Optional

from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.register import Form
from tracardi.service.utils.hasher import uuid4_from_md5


class Bridge(NamedEntity):
    description: Optional[str] = ""
    type: str
    config: Optional[dict] = {}
    form: Optional[Form] = None
    manual: Optional[str] = None

    def get_id_in_context_of_tenant(self, context) -> str:
        id_in_context_of_tenant = md5(f"{self.id}-{context.tenant}".encode()).hexdigest()
        return uuid4_from_md5(id_in_context_of_tenant)
