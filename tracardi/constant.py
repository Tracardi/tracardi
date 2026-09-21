import os

# This is important _FORCE_SINGLE_INDICES = yes, will keep all data in test indices
# regardless of mode. But all configurations will be kept in a sandbox.

PRODUCTION_INDEX_PREFIX = None if os.environ.get('_FORCE_SINGLE_INDICES', None) == 'yes' else 'prod-'