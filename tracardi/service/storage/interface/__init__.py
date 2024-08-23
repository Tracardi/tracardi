from tracardi.config import tracardi

if tracardi.storage_driver == 'elasticsearch':
    from tracardi.service.storage.elastic.interface.collector.mutation import profile as profile_mutation_collector_dao
    from tracardi.service.storage.elastic.interface.collector.load import profile as profile_load_collector_dao
    from tracardi.service.storage.elastic.interface.gui import profile as profile_gui_dao
elif tracardi.storage_driver == 'starrocks':
    from com_tracardi.storage.starrocks.interface.collector.mutation import profile as profile_mutation_collector_dao
    from com_tracardi.storage.starrocks.interface.collector.load import profile as profile_load_collector_dao
    from com_tracardi.storage.starrocks.interface.gui import profile as profile_gui_dao
else:
    raise ValueError(f"Unknown storage driver: {tracardi.storage_driver}")

__all__ = ['profile_mutation_collector_dao', 'profile_load_collector_dao', 'profile_gui_dao']
