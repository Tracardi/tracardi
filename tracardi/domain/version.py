from pydantic import BaseModel


class Version(BaseModel):
    prev_version: 'Version' = None
    version: str
    name: str

    def get_version_prefix(self):
        return self.version.replace(".", "")

    def get_head_with_prev_version(self, prev: 'Version'):
        version_copy = Version(**self.dict())
        version_copy.prev_version = Version(
            version=prev.version,
            name=prev.name
        )

        return version_copy

    def has_prev_version(self):
        return self. prev_version is not None

    def __eq__(self, other):
        return other and self.version == other.version and self.name == other.name \
               and self.prev_version.version == other.prev_version.version \
               and self.prev_version.name == other.prev_version.name

    def __str__(self):
        return f"Version {self.version}.{self.name} ({self.prev_version.version if self.prev_version else 'No previous version'})"
