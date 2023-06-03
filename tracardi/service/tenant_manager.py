from typing import Optional

from tracardi.config import tracardi
from tracardi.service.string_manager import remove_non_alpha


def get_tenant_name_from_host(hostname) -> Optional[str]:
    parts = hostname.split(".")
    if len(parts) >= 3:
        _tenant_candidate = remove_non_alpha(parts[0])
        if len(_tenant_candidate) >= 3 and not _tenant_candidate.isnumeric():
            return _tenant_candidate
    return None


def get_tenant_name_from_scope(scope) -> Optional[str]:
    tenant = None
    if tracardi.multi_tenant:
        if 'headers' in scope:
            headers = {item[0].decode(): item[1].decode() for item in scope['headers']}
            if 'host' in headers:
                hostname = headers['host']
                hostname = hostname.split(":")[0]
                if hostname in ['localhost', '0.0.0.0', '127.0.0.1']:
                    tenant = tracardi.version.name
                else:
                    parts = hostname.split(".")
                    if len(parts) >= 3:
                        _tenant_candidate = remove_non_alpha(parts[0])
                        if len(_tenant_candidate) >= 3 and not _tenant_candidate.isnumeric():
                            tenant = _tenant_candidate
    else:
        tenant = tracardi.version.name

    return tenant
