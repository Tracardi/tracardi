import os

package_name = os.getenv('STORAGE_DRIVER', 'elasticsearch')

if package_name == 'elasticsearch':
    import tracardi.service.storage.interface.elastic as dao
elif package_name == 'starrocks':
    import tracardi.service.storage.interface.starrocks as dao
else:
    raise ValueError(f"Unknown storage driver: {package_name}")

__all__ = ['dao']