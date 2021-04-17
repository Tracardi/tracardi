from ... import config
from ...domain.segment import Segment


def upsert_segment(elastic, q, segment: Segment):
    segment_index = config.index['segments']
    segment = {
        '_id': segment.get_id(),
        'uql': q,
        'scope': segment.scope,
        'name': segment.name,
        'description': segment.description,
        'condition': segment.condition
    }
    return elastic.insert(segment_index, [segment])

