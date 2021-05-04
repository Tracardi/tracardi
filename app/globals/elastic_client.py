from .. import config
from ..storage.elasticsreach import Elastic
from ssl import create_default_context

_singleton = None


def elastic_client():
    global _singleton

    def get_elastic_client():

        kwargs = {}

        if config.elastic.host:
            kwargs['hosts'] = config.elastic.host
        if config.elastic.scheme:
            kwargs['scheme'] = config.elastic.scheme
        if config.elastic.sniffer_timeout:
            kwargs['sniffer_timeout'] = config.elastic.sniffer_timeout
        if config.elastic.sniff_on_start:
            kwargs['sniff_on_start'] = config.elastic.sniff_on_start
        if config.elastic.sniff_on_connection_fail:
            kwargs['sniff_on_connection_fail'] = config.elastic.sniff_on_connection_fail
        if config.elastic.maxsize:
            kwargs['maxsize'] = config.elastic.maxsize

        if config.elastic.cafile:
            context = create_default_context(cafile=config.elastic.cafile)
            kwargs['ssl_context'] = context

        if config.elastic.http_auth_password and config.elastic.http_auth_username:
            kwargs['http_auth'] = (config.elastic.http_auth_username, config.elastic.http_auth_password)

        if config.elastic.cloud_id:
            kwargs['cloud_id'] = config.elastic.cloud_id

        if config.elastic.api_key:
            kwargs['api_key'] = config.elastic.api_key

        if config.elastic.http_compress:
            kwargs['http_compress'] = config.elastic.http_compress

        return Elastic(**kwargs)

    if _singleton is None:
        _singleton = get_elastic_client()

    return _singleton
