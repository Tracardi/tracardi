# from tracardi.config import tracardi
#
# if tracardi.big_data_adapter.lower() == 'elastic':
#     from tracardi.service.dependency.adapters.elastic import *
# elif tracardi.big_data_adapter.lower() == 'starrocks':
#     from tracardi.service.dependency.adapters.elastic import *
# else:
#     raise ValueError(f"Unknown big data adapter `{tracardi.big_data_adapter}`")
#
# if tracardi.meta_data_adapter.lower() == 'mysql':
#     from tracardi.service.dependency.adapters.mysql import *
# else:
#     raise ValueError(f"Unknown meta data adapter `{tracardi.meta_data_adapter}`")