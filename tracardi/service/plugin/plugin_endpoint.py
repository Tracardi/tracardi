class PluginEndpoint:

    @staticmethod
    def url(module, endpoint):
        return f"/plugin/{module}/{endpoint}"
