import os
from tracardi.domain.version import Version
from tracardi.service.utils.environment import get_env_as_bool

VERSION = os.environ.get('_DEBUG_VERSION', '1.1.x')
TENANT_NAME = os.environ.get('TENANT_NAME', None)
PRODUCTION = os.environ.get('PRODUCTION', 'no').lower() == 'yes'
MULTI_TENANT = get_env_as_bool('MULTI_TENANT', "no")

version:Version = Version(version=VERSION, name=TENANT_NAME, production=PRODUCTION, multi_tenant=MULTI_TENANT)