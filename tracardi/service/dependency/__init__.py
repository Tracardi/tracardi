from tracardi.config import tracardi

if tracardi.big_data_adapter.lower() == 'elastic':
    from .adapters.elastic import *
else:
    raise ValueError(f"Unknown big data adapter `{tracardi.big_data_adapter}`")