from tracardi.service.storage.elastic_client import ElasticClient

es = ElasticClient.instance()


async def create_snapshot_repository(repo, setting):
    return await es.create_snapshot_repository(repo, setting)


async def get_snapshot_repository(repo):
    return await es.get_snapshot_repository(repo)


async def delete_snapshot_repository(repo):
    return await es.delete_snapshot_repository(repo)


async def get_repository_snapshots(repo):
    return await es.get_repository_snapshots(repo)


async def get_snapshot(repo, snapshot):
    return await es.get_snapshot(repo, snapshot)


async def get_snapshot_status(repo, snapshot):
    return await es.get_snapshot_status(repo, snapshot)


async def delete_snapshot(repo, snapshot):
    return await es.delete_snapshot(repo, snapshot)


async def create_snapshot(repo, snapshot, setting=None, params=None):
    return await es.create_snapshot(repo, snapshot, body=setting, params=params)


async def restore_snapshot(repo, snapshot, setting=None, params=None):
    return await es.restore_snapshot(repo, snapshot, body=setting, params=params)
