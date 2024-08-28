from typing import Optional, List

from pydantic import BaseModel


class SystemInstallationStatus(BaseModel):
    schema_ok: bool = False
    admin_ok: Optional[bool] = None
    form_ok: Optional[bool] = None
    warning: Optional[List[str]] = None
    config: Optional[dict] = {}
