from typing import Optional, Tuple
from urllib.parse import urlparse
from tracardi.config import tracardi
from tracardi.service.string_manager import remove_non_alpha


def get_tenant_name_from_host(hostname) -> Optional[str]:
    parts = hostname.split(".")
    if len(parts) >= 3:
        _tenant_candidate = remove_non_alpha(parts[0])
        if len(_tenant_candidate) >= 3 and not _tenant_candidate.isnumeric():
            return _tenant_candidate
    return None


def get_hostname_from_scope(scope) -> Optional[str]:
    if 'headers' in scope:
        headers = {item[0].decode(): item[1].decode() for item in scope['headers']}
        scheme = headers.get('scheme', 'http')
        if 'host' in headers:
            hostname = headers['host']
            return f"{scheme}://{hostname}"
    return None


def get_tenant_name_from_scope(scope) -> Tuple[Optional[str], Optional[str]]:
    tenant = None
    hostname = get_hostname_from_scope(scope)
    if hostname and tracardi.multi_tenant:
        host = urlparse(hostname)
        domain = host.netloc.split(":")[0]  # type: str
        if domain in ['localhost', '0.0.0.0', '127.0.0.1']:
            tenant = tracardi.version.name
        else:
            parts = domain.split(".")
            if len(parts) >= 3:
                _tenant_candidate = remove_non_alpha(parts[0])
                if len(_tenant_candidate) >= 3 and not _tenant_candidate.isnumeric():
                    tenant = _tenant_candidate
    else:
        tenant = tracardi.version.name

    return tenant, hostname
