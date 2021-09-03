from tracardi.domain.entity import Entity
from tracardi.domain.resource import ResourceRecord, Resource


async def read_source(resource_id: str) -> Resource:
    """
    Reads source by source id
    :param resource_id: str
    :return source: Source
    """

    resource_config_record = await Entity(id=resource_id). \
        storage('resource'). \
        load(ResourceRecord)  # type: ResourceRecord

    if resource_config_record is None:
        raise ValueError('Resource id {} does not exist.'.format(resource_id))

    return resource_config_record.decode()
