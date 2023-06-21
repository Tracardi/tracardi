from typing import Optional, Tuple
from tracardi.config import tracardi


def get_hostname_from_scope(scope) -> Optional[str]:
    if 'headers' in scope:
        headers = {item[0].decode(): item[1].decode() for item in scope['headers']}
        scheme = headers.get('scheme', 'http')
        if 'host' in headers:
            hostname = headers['host']
            return f"{scheme}://{hostname}"
    return None


def get_tenant_name_from_scope(scope) -> Tuple[Optional[str], Optional[str]]:
    return tracardi.version.name, get_hostname_from_scope(scope)
