from tracardi.service.storage.elastic.driver.elastic_client import ElasticClient


async def elastic_close():
    elastic = ElasticClient.instance()
    await elastic.close()