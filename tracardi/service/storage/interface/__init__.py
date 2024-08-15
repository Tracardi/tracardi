from tracardi.config import tracardi

if tracardi.storage_driver == 'elasticsearch':
    from tracardi.service.storage.interface.elastic.collector.mutation import profile as profile_mutation_dao
elif tracardi.storage_driver == 'starrocks':
    from tracardi.service.storage.interface.starrocks.collector.mutation import profile as profile_mutation_dao
else:
    raise ValueError(f"Unknown storage driver: {tracardi.storage_driver}")

__all__ = ['profile_mutation_dao']
