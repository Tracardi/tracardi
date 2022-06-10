from typing import Optional

from pydantic import BaseModel


class SubVersion(BaseModel):
    version: str
    name: str


class Version(BaseModel):
    prev_version: Optional[SubVersion] = None
    version: str
    name: str

    def get_version_prefix(self):
        return self.version.replace(".", "")

    def get_head_with_prev_version(self, prev: 'Version'):
        version_copy = self.copy(update={'prev_version': None})
        version_copy.prev_version = SubVersion(
            version=prev.version,
            name=prev.name
        )

        return version_copy

    def has_prev_version(self):
        return self.prev_version is not None

    def __eq__(self, other):
        return other and self.version == other.version and self.name == other.name

    def __str__(self):
        return f"Version {self.version}.{self.name} ({self.prev_version.version if isinstance(self.prev_version, SubVersion) else 'No previous version'})"
