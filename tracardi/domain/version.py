from pydantic import BaseModel


class Version(BaseModel):
    prev_version: 'Version' = None
    version: str
    name: str

    def get_version_prefix(self):
        return self.version.replace(".", "")

    def get_head_with_prev_version(self, prev: 'Version'):
        version_copy = self.copy(update={'prev_version': None})
        version_copy.prev_version = Version(
            version=prev.version,
            name=prev.name
        )

        return version_copy

    def has_prev_version(self):
        return self. prev_version is not None

    def __eq__(self, other):
        return other and self.version == other.version and self.name == other.name

    def __str__(self):
        return f"Version {self.version}.{self.name} ({self.prev_version.version if isinstance(self.prev_version, Version) else 'No previous version'})"
