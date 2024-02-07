from typing import List, Optional

from pydantic import BaseModel


class InstallationStatus(BaseModel):
    schema_ok: bool =  False
    admin_ok: bool = False
    form_ok: bool = False
    warning: Optional[List[str]] = None

    def is_installed(self) -> bool:
        return self.schema_ok and self.admin_ok and self.form_ok
