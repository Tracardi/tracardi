from tracardi.config import tracardi

if tracardi.storage_driver == 'elasticsearch':
    from tracardi.service.storage.interface.elastic.collector.mutation import profile as profile_mutation_dao
    from tracardi.service.storage.interface.elastic.collector.load import profile as profile_load_dao
elif tracardi.storage_driver == 'starrocks':
    from com_tracardi.storage.starrocks.interface.collector.mutation import profile as profile_mutation_dao
    from com_tracardi.storage.starrocks.interface.collector.load import profile as profile_load_dao
else:
    raise ValueError(f"Unknown storage driver: {tracardi.storage_driver}")

__all__ = ['profile_mutation_dao', 'profile_load_dao']
