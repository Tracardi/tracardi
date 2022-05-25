from pydantic import BaseModel


class Version(BaseModel):
    version: str
    name: str

    def get_version_prefix(self):
        return self.version.replace(".", "")

    def prefix_index_with_version(self, index, as_template=False):
        if as_template:
            return f"{self.get_version_prefix()}.{self.name}-{index}-*-*"
        return f"{self.get_version_prefix()}.{self.name}-{index}"

    def __str__(self):
        return self.version
