import os

package_name = os.getenv('STORAGE_DRIVER', 'starrocks')

if package_name == 'elasticsearch':
    from tracardi.service.storage.interface.elastic.collector.mutation import profile as profile_mutation_dao
elif package_name == 'starrocks':
    from tracardi.service.storage.interface.starrocks.collector.mutation import profile as profile_mutation_dao
else:
    raise ValueError(f"Unknown storage driver: {package_name}")

__all__ = ['profile_mutation_dao']
