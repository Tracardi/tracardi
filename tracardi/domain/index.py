import logging
from datetime import datetime

from tracardi.domain.query_result import QueryResult
from tracardi.domain.time_range_query import DatetimeRangePayload
from tracardi.event_server.service.persistence_service import PersistenceService
from tracardi.exceptions.exception import StorageException
from tracardi.service.storage import index as index_2_elastic
from tracardi.service.storage.elastic_storage import ElasticStorage
from tracardi.service.storage.sql import to_sql_query, to_time_range_sql_query

_logger = logging.getLogger("Index")


class Index:

    def __init__(self, index: str):
        self.index = index
        self.read_index = index_2_elastic.resources[index].get_read_index()
        self.storage_service = PersistenceService(ElasticStorage(index_key=self.index))
        self.time_fields_map = {
            'event': 'metadata.time.insert',
            'session': 'metadata.time.insert',
            'profile': 'metadata.time.insert',
        }

    async def search(self, query: str = None, limit: int = 20):
        query = to_sql_query(self.read_index, query=query, limit=limit)
        return (await self.storage_service.sql(query)).dict()

    @staticmethod
    def _convert_time_zone(query, min_date_time, max_date_time):
        time_zone = "UTC" if query.timeZone is None or query.timeZone == "" else query.timeZone

        if time_zone != "UTC":
            min_date_time, time_zone = query.convert_to_local_datetime(min_date_time, time_zone)
            max_date_time, time_zone = query.convert_to_local_datetime(max_date_time, time_zone)

        return min_date_time, max_date_time, time_zone

    async def time_range(self, query: DatetimeRangePayload) -> QueryResult:

        if self.index not in self.time_fields_map:
            raise ValueError("No time_field available on `{}`".format(self.index))

        min_date_time, max_date_time = query.get_dates()  # type: datetime, datetime
        min_date_time, max_date_time, time_zone = self._convert_time_zone(query, min_date_time, max_date_time)

        limit = query.limit
        offset = query.offset
        sql = query.where
        time_field = self.time_fields_map[self.index]

        sql = to_time_range_sql_query(self.read_index, time_field, min_date_time, max_date_time, sql)
        try:
            translated_query = await self.storage_service.translate(sql)
        except StorageException as e:
            _logger.error("Could not translate SQL {}. Reason: {}".format(sql, str(e)))
            return QueryResult(total=0, result=[])

        # Add time zone

        if time_zone:
            if 'range' in translated_query['query']:
                translated_query['query']['range'][time_field]['time_zone'] = time_zone
            elif 'bool' in translated_query['query'] and 'must' in translated_query['query']['bool']:
                translated_query['query']['bool']['must'][0]['range'][time_field]['time_zone'] = time_zone

        es_query = {
            "from": offset,
            "size": limit,
            "query": translated_query['query'],
            "sort": [
                {
                    time_field: "desc"
                }
            ]
        }

        try:
            result = await self.storage_service.filter(es_query)
        except StorageException as e:
            _logger.error("Could not filter {}. Reason: {}".format(es_query, str(e)))
            return QueryResult(total=0, result=[])

        return QueryResult(**result.dict())

    async def histogram(self, query: DatetimeRangePayload):

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
                # todo timestamp no timezone
                timestamp = datetime.fromisoformat(row["key_as_string"].replace('Z', '+00:00'))
                yield {
                    "time": "{}".format(timestamp.strftime(format)),
                    'interval': "+{}{}".format(interval, unit),
                    "events": row["doc_count"]
                }

        min_date_time, max_date_time = query.get_dates()  # type: datetime, datetime
        min_date_time, max_date_time, time_zone = self._convert_time_zone(query, min_date_time, max_date_time)

        # limit = query.limit
        # offset = query.offset
        sql = query.where
        time_field = self.time_fields_map[self.index]

        interval, unit, format = __interval(min_date_time, max_date_time)

        sql = to_time_range_sql_query(self.read_index, time_field, min_date_time, max_date_time, sql)

        try:
            translated_query = await self.storage_service.translate(sql)
        except StorageException as e:
            _logger.error("Could not translate SQL {}. Reason: {}".format(sql, str(e)))
            return QueryResult(total=0, result=[])

        if time_zone:
            if 'range' in translated_query['query']:
                translated_query['query']['range'][time_field]['time_zone'] = time_zone
            elif 'bool' in translated_query['query'] and 'must' in translated_query['query']['bool']:
                translated_query['query']['bool']['must'][0]['range'][time_field]['time_zone'] = time_zone

        es_query = {
            "size": 0,
            "query": translated_query['query'],
            "aggs": {
                "items_over_time": {
                    "date_histogram": {
                        "min_doc_count": 0,
                        "field": time_field,
                        "fixed_interval": f"{interval}{unit}",
                        "extended_bounds": {
                            "min": min_date_time,
                            "max": max_date_time
                        }
                    }
                }
            }
        }

        if time_zone:
            es_query['aggs']['items_over_time']['date_histogram']['time_zone'] = time_zone

        try:
            result = await self.storage_service.query(es_query)
        except StorageException as e:
            _logger.error("Could not query {}. Reason: {}".format(es_query, str(e)))
            return QueryResult(total=0, result=[])

        qs = {
            'total': result['hits']['total']['value'],
            'result': list(__format(result['aggregations']['items_over_time']['buckets'], unit, interval, format))
        }

        return QueryResult(**qs)
