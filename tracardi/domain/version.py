from pydantic import BaseModel, validator
from typing import Optional, List
from hashlib import md5


class Version(BaseModel):
    version: str
    name: Optional[str] = None
    upgrades: List[str] = []
    production: bool = False
    config: Optional[dict] = {}

    @validator("name")
    def validate_prefix(cls, value, values):
        return value if value is not None else Version.generate_name(values["version"])

    @staticmethod
    def generate_name(version):
        return md5(version.encode('utf-8')).hexdigest()[:5]

    @staticmethod
    def generate_prefix(version):
        return version.replace(".", "")

    def get_version_prefix(self):
        """
        e.g. 070
        """
        version_prefix = Version.generate_prefix(self.version)
        return version_prefix

    def __eq__(self, other: 'Version') -> bool:
        return other and self.version == other.version and self.name == other.name

    def __str__(self):
        return f"Version {self.version}.{self.name}"

    def add_upgrade(self, name: str) -> None:
        upgrades = set(self.upgrades)
        upgrades.add(name)
        self.upgrades = list(upgrades)
