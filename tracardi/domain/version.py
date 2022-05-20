class Version:

    def __init__(self, version):
        self.version = version

    def get_version_prefix(self):
        return self.version.replace(".", "")

    def __str__(self):
        return self.version
