from .. import config
from ..storage.elasticsreach import Elastic

_singleton = None


def elastic_client():
    global _singleton

    def get_elastic_client():
        return Elastic(config.elastic['host'], port=config.elastic['port'])

    if _singleton is None:
        _singleton = get_elastic_client()

    return _singleton
