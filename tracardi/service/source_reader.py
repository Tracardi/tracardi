from tracardi.domain.entity import Entity
from tracardi.domain.source import SourceRecord, Source


async def read_source(source_id: str) -> Source:
    """
    Reads source by source id
    :param source_id: str
    :return source: Source
    """

    source_config_record = await Entity(id=source_id). \
        storage('source'). \
        load(SourceRecord)  # type: SourceRecord

    if source_config_record is None:
        raise ValueError('Source id {} does not exist.'.format(source_id))

    return source_config_record.decode()
