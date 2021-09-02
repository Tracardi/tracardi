from tracardi.domain.entity import Entity
from tracardi.domain.source import SourceRecord


def source_reader(source_id):
    source_config_record = await Entity(id=source_id). \
        storage('source'). \
        load(SourceRecord)  # type: SourceRecord

    if source_config_record is None:
        raise ValueError('Source id {} does not exist.'.format(source_id))

    return source_config_record.decode()
