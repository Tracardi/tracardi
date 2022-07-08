from typing import Optional

from pydantic import BaseModel


class SnapshotRepoSettings(BaseModel):
    chunk_size: Optional[int] = None
    compress: bool = True
    max_number_of_snapshots: int = 500
    readonly: bool = False
    location: str
    delegate_type: Optional[str] = 'fs'  # Available fs, url, source
    verify: bool = True


class SnapshotRepo(BaseModel):
    type: str = 'fs'
    settings: SnapshotRepoSettings
