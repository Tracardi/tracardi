from tracardi.config import tracardi
from tracardi.service.storage.elastic_client import ElasticClient


class InstallationStatus(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.es = ElasticClient.instance()

    async def has_logs_index(self, tenant):
        if tenant not in self or self[tenant] is False:
            self[tenant] = await self.es.exists_index_template(f'prod-{tracardi.version.db_version}.{tenant}.tracardi-log')

        return self[tenant]


installation_status = InstallationStatus()