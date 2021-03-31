from ..globals.context_server_host import get_context_server_host
from ..uql.uql import UQL

_singleton = None


def context_server_via_uql():
    global _singleton

    def get_parser():
        host = get_context_server_host()
        return UQL(host)

    if _singleton is None:
        _singleton = get_parser()

    return _singleton
