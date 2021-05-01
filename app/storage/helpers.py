from datetime import datetime
from pprint import pprint

import elasticsearch
from fastapi import HTTPException

from app import config
from app.storage.sql import to_sql


def update_record(elastic, index, id, record):
    try:
        return elastic.update(index, id, record)
    except elasticsearch.exceptions.TransportError as e:
        raise HTTPException(status_code=e.status_code, detail=e.info)


def data_histogram(elastic, index, group_by, min: datetime, max: datetime, time_zone: str = None, query: str = ""):
    def __interval(min: datetime, max: datetime):

        max_interval = 50
        min_interval = 20

        span = max - min

        if span.days > max_interval:
            # up
            return int(span.days / max_interval), 'd', "%y-%m-%d"
        elif min_interval > span.days:
            # down
            interval = int((span.days * 24) / max_interval)
            if interval > 0:
                return interval, 'h', "%d/%m %H:%M"

            # minutes
            interval = int((span.days * 24 * 60) / max_interval)
            if interval > 0:
                return interval, 'm', "%H:%M"

            return 1, 'm', "%H:%M"

        return 1, 'd', "%y-%m-%d"

    def __format(data, unit, interval, format):
        for row in data:
            timestamp = datetime.fromisoformat(row["key_as_string"].replace('Z', '+00:00'))
            yield {
                "time": "{}".format(timestamp.strftime(format)),
                'interval': "+{}{}".format(interval, unit),
                "events": row["doc_count"]
            }

    interval, unit, format = __interval(min, max)
    event_index = config.unomi_index[index]
    query = to_sql(event_index, group_by, min, max, query)

    translated_query = elastic.sql.translate(query)

    if time_zone:
        if 'range' in translated_query['query']:
            translated_query['query']['range'][group_by]['time_zone'] = time_zone
        elif 'bool' in translated_query['query'] and 'must' in translated_query['query']['bool']:
            translated_query['query']['bool']['must'][0]['range'][group_by]['time_zone'] = time_zone

    query = {
        "size": 0,
        "query": translated_query['query'],
        "aggs": {
            "items_over_time": {
                "date_histogram": {
                    "min_doc_count": 0,
                    "field": group_by,
                    "fixed_interval": f"{interval}{unit}",
                    "extended_bounds": {
                        "min": min,
                        "max": max
                    }
                }
            }
        }
    }

    if time_zone:
        query['aggs']['items_over_time']['date_histogram']['time_zone'] = time_zone

    pprint(query)

    result = elastic.search(event_index, query)

    return {
        'total': result['hits']['total']['value'],
        'data': list(__format(result['aggregations']['items_over_time']['buckets'], unit, interval, format))
    }


def object_data(elastic, index, group_by, from_date_time: datetime, to_date_time: datetime,
                offset: int = 0,
                limit: int = 20,
                time_zone: str = None,
                query: str = ""):
    index = config.unomi_index[index]
    query = to_sql(index, group_by, from_date_time, to_date_time, query)
    translated_query = elastic.sql.translate(query)

    # Add time zone

    if time_zone:
        if 'range' in translated_query['query']:
            translated_query['query']['range'][group_by]['time_zone'] = time_zone
        elif 'bool' in translated_query['query'] and 'must' in translated_query['query']['bool']:
            translated_query['query']['bool']['must'][0]['range'][group_by]['time_zone'] = time_zone

    query = {
        "from": offset,
        "size": limit,
        "query": translated_query['query'],
        "sort": [
            {
                group_by: "desc"
            }
        ]
    }


    pprint(query)
    result = elastic.search(index, query)

    return {
        'total': result['hits']['total']['value'],
        'data': [row['_source'] for row in result['hits']['hits']]
    }
